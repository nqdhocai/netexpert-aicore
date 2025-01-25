import random
import pandas as pd
from components.database.database import get_all_devices
import re

def create_population(data, population_size, num_devices, vlan_requirement, poe_devices, bandwidth_estimation):
    population = []
    for _ in range(population_size):
        routers = data[data['device_type'] == 'router'].to_dict('records')
        modems = data[data['device_type'] == 'modem'].to_dict('records')
        switches = data[data['device_type'] == 'switch'].to_dict('records')
        access_points = data[data['device_type'] == 'access point'].to_dict('records')

        # Chọn thiết bị dựa trên các ràng buộc
        solution = [
            random.choice(routers),
            random.choice(modems),
            *[random.choice(switches) for _ in range(max(1, int(num_devices) // 24))],  # 24 devices per switch
            *[random.choice(access_points) for _ in range(max(1, poe_devices))]  # POE devices
        ]
        population.append(solution)
    return population
def mutate(solution, data, mutation_rate):
    for i in range(len(solution)):
        if random.random() < mutation_rate:
            device_type = solution[i]['device_type']
            devices = data[data['device_type'] == device_type].to_dict('records')
            solution[i] = random.choice(devices)
    return solution
def crossover(parent1, parent2):
    child = []
    for i in range(len(parent1)):
        child.append(random.choice([parent1[i], parent2[i]]))
    return child
def selection(population, fitness_scores, num_parents):
    parents = []
    for _ in range(num_parents):
        max_index = fitness_scores.index(max(fitness_scores))
        parents.append(population[max_index])
        fitness_scores[max_index] = -1
    return parents
def fitness_function(solution, budget, num_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level):
    total_cost = sum(float(device['price']) for device in solution)
    total_bandwidth = sum(device['bandwidth'] for device in solution if pd.notna(device['bandwidth']))
    vlan_support = all((vlan_requirement.lower() == 'yes')or(vlan_requirement in device['vlan_support']) for device in solution if pd.notna(device['vlan_support']))
    poe_support = sum(1 for device in solution if device['poe_support'] == 'Yes') >= poe_devices
    security_match = all(security_level.lower() in device['security_features'].lower() for device in solution if pd.notna(device['security_features']))

    # Kiểm tra ràng buộc
    if (total_cost > budget*120/100):
        return 0

    # Tính điểm
    score = (
        0.2 * float(float(total_bandwidth) / float(bandwidth_estimation)) +
        0.7 * (1 - (total_cost / budget)) +
        0.1 * (1 if vlan_support else 0) +
        0.1 * (1 if security_match else 0)
    )
    return score

def genetic_algorithm(data, budget, num_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level,
                      population_size, num_generations, mutation_rate):
    population = create_population(data, population_size, num_devices, vlan_requirement, poe_devices, bandwidth_estimation)

    for generation in range(num_generations):
        fitness_scores = [
            fitness_function(solution, budget, num_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level)
            for solution in population]

        parents = selection(population, fitness_scores, population_size // 2)

        offspring = []
        while len(offspring) < population_size - len(parents):
            parent1, parent2 = random.sample(parents, 2)
            child = crossover(parent1, parent2)
            child = mutate(child, data, mutation_rate)
            offspring.append(child)

        population = parents + offspring

    best_solution = max(population,
                        key=lambda x: fitness_function(x, budget, num_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level))
    return best_solution

def get_business_network_solution(budget, num_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level):
    data = pd.DataFrame(get_all_devices())
    population_size = 50
    num_generations = 100
    mutation_rate = 0.1
    best_solution = genetic_algorithm(data, budget, num_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level,
                                      population_size, num_generations, mutation_rate)
    for device in best_solution:
        if 'embedding' in device.keys():
            del device['embedding']
    return best_solution