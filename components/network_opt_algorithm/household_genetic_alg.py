import random
import pandas as pd
from components.database.database import get_device_by_location, get_all_devices
import re

# Hàm tạo quần thể
def create_population(data, population_size, num_devices, coverage_required):
    population = []
    for _ in range(population_size):
        avg_coverage_per_ap = 150
        num_ap = max(1, round(coverage_required / avg_coverage_per_ap))

        avg_devices_per_switch = 24
        num_switch = max(1, round(num_devices / avg_devices_per_switch))

        routers = data[data['device_type'] == 'router'].to_dict('records')
        modems = data[data['device_type'] == 'modem'].to_dict('records')
        switches = data[data['device_type'] == 'switch'].to_dict('records')
        access_points = data[data['device_type'] == 'access point'].to_dict('records')

        solution = [
            random.choice(routers),
            random.choice(modems),
            *[random.choice(switches) for _ in range(num_switch)],
            *[random.choice(access_points) for _ in range(num_ap)]
        ]
        population.append(solution)
    return population


# Hàm đánh giá
def fitness_function(solution, budget, num_devices, coverage_required, preferred_frequency, brand_preference): #[TODO] fix the fitness function to use data type of preferred_frequency as NUMBER
    total_cost = sum(device['price'] for device in solution)
    total_devices_supported = sum(
        int(re.findall(r'\d+', device['max_devices_supported'])[0]) for device in solution if len(re.findall(r'\d+', device['max_devices_supported'])) > 0)
    total_coverage = sum(int(re.findall(r'\d+', device['coverage'])[0]) for device in solution if len(re.findall(r'\d+', device['coverage']))>0)
    frequency_supported = all(
        preferred_frequency in device['frequency'] for device in solution if 'frequency' in device)
    brand_match = all(device['manufacturer'] in brand_preference for device in solution) if brand_preference else True

    if total_cost > budget or total_devices_supported < num_devices or total_coverage < coverage_required or not frequency_supported:
        return 0

    score = (
            0.3 * (total_devices_supported / num_devices) +
            0.3 * (total_coverage / coverage_required) +
            0.2 * (1 - (total_cost / budget)) +
            0.1 * (1 if brand_match else 0) +
            0.1 * (1 if frequency_supported else 0)
    )
    return score


# Hàm chọn lọc
def selection(population, fitness_scores, num_parents):
    parents = []
    for _ in range(num_parents):
        max_index = fitness_scores.index(max(fitness_scores))
        parents.append(population[max_index])
        fitness_scores[max_index] = -1
    return parents


# Hàm lai ghép
def crossover(parent1, parent2):
    child = []
    for i in range(len(parent1)):
        child.append(random.choice([parent1[i], parent2[i]]))
    return child


# Hàm đột biến
def mutate(solution, data, mutation_rate):
    for i in range(len(solution)):
        if random.random() < mutation_rate:
            device_type = solution[i]['device_type']
            devices = data[data['device_type'] == device_type].to_dict('records')
            solution[i] = random.choice(devices)
    return solution


# Thuật toán GA
def genetic_algorithm(data, budget, num_devices, coverage_required, preferred_frequency, brand_preference,
                      population_size, num_generations, mutation_rate):
    population = create_population(data, population_size, num_devices, coverage_required)

    for generation in range(num_generations):
        fitness_scores = [
            fitness_function(solution, budget, num_devices, coverage_required, preferred_frequency, brand_preference)
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
                        key=lambda x: fitness_function(x, budget, num_devices, coverage_required, preferred_frequency,
                                                       brand_preference))
    return best_solution

def get_household_network_solution(budget, num_devices, coverage_required, preferred_frequency, brand_preference, nation, province):
    if province == "" or nation=="Global":
        devices = get_all_devices()
    else:
        devices = get_device_by_location(nation, province)
    if devices is None:
        devices = get_all_devices()
        
    data = pd.DataFrame(devices)
    population_size = 50
    num_generations = 100
    mutation_rate = 0.1
    best_solution = genetic_algorithm(data, budget, num_devices, coverage_required, preferred_frequency,
                                      brand_preference,
                                      population_size, num_generations, mutation_rate)
    print("Best solution:")
    for device in best_solution:
        if 'embedding' in device.keys():
            del device['embedding']
    return best_solution
