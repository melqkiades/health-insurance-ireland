import json
import time
from os import walk

import pandas
import requests
from tqdm import tqdm

DATA_FOLDER = '/Users/fpena/Projects/hia/data/manually_collected/'

def load_benefits():
    json_template_file = DATA_FOLDER + 'vhi_pmi_39_14.json'
    with open(json_template_file) as of:
        template_data = json.load(of)

    benefits_map = {}
    my_benefits_list = []

    for benefits_list in template_data['data']['benefits_sections']:
        for benefit in benefits_list['benefits']:
            benefits_map[benefit['id']] = benefit
            my_benefits_list.append(benefit)

    # for benefit in benefits_map.values():
    #     print(benefit['id'], benefit['name'])

    return benefits_map

BENEFITS_DICT = load_benefits()


def download_plans():

    MIN_ID = 1
    MAX_ID = 860
    url = 'https://api.hia.ie/api/plans/{}'
    sucess_code = 200
    not_found_code = 404

    plans = []

    for id in tqdm(range(MIN_ID, MAX_ID)):
        request = requests.get(url.format(id))
        status_code = request.status_code
        print(status_code)

        while status_code == 429:
            time.sleep(30)
            request = requests.get(url.format(id))
            status_code = request.status_code
            print(status_code)
        # json_data = request.json()
        # print(url.format(id))
        # print(request.json())
        if request.status_code == sucess_code:
            json_data = request.json()
            plan = process_plan(json_data)
            plans.append(plan)
        else:
            print(request.status_code)
            print(url.format(id))

    data_frame = pandas.DataFrame(plans)

    print(data_frame.head())
    print(data_frame.describe())
    data_frame.to_csv('/Users/fpena/Projects/hia/data/automatic_plans.csv', sep='\t', encoding='utf-8')


def process_plan(json_data):

    plan_id = json_data['data']['id']
    name = json_data['data']['name']
    price = json_data['data']['priceOptions'][0]['value']
    insurer = json_data['data']['insurer']['name']
    publication_date = json_data['data']['publication_date']
    plan_benefits = json_data['data']['planBenefits']
    # print(benefits)
    plan_benefits_map = {}
    for benefit in plan_benefits:
        plan_benefits_map[benefit['benefit_id']] = benefit
    # print(benefits_map)

    # print('Plan: ' + name)
    # print('Price: ' + str(price) + ' per/month: ' + str(price/12))
    # print('Insurer: ' + insurer)
    # print('Date: ' + publication_date)
    # print('')
    #
    # benefits_map = load_benefits()
    # highlighted_benefits = [45, 88, 135, 153, 225, 226, 227]
    #
    # for benefit_id in highlighted_benefits:
    #     print(benefit_id, benefits_map[benefit_id]['name'], plan_benefits_map[benefit_id]['variable'])
    # print('')
    #
    # for benefit in plan_benefits:
    #     benefit_id = benefit['benefit_id']
    #     print(benefit_id, benefits_map[benefit_id]['name'], benefit['variable'])

    plan = {
        'plan_id': plan_id,
        'name': name,
        'price': price,
        'insurer': insurer,
        'publication_date': publication_date,
    }

    for benefit in BENEFITS_DICT.values():
        benefit_id = benefit['id']
        benefit_name = benefit['name']
        plan[benefit_name] = plan_benefits_map[benefit_id]['variable'] if benefit_id in plan_benefits_map else 'N/A'
        plan[benefit_name] = plan[benefit_name].encode('utf-8') if plan[benefit_name] is not None else 'None'
        plan[benefit_name] = plan[benefit_name].replace('\n', '')

    return plan


def export_plan(plans):

    benefits_dict = load_benefits()

    for plan in plans:
        for benefit in benefits_dict.values():
            benefit_id = benefit['id']
            benefit_name = benefit['name']


def load_all_benefits():

    plans_folder = DATA_FOLDER + 'prices/'
    plan_files = files_in_folder(plans_folder)
    plans = []

    for plan_file in plan_files:
        with open(plans_folder + plan_file) as of:
            json_data= json.load(of)
        plan = process_plan(json_data)
        # consultant = plan['benefits'][45]['variable']
        # gp = plan['benefits'][88]['variable'] if 88 in plan['benefits'] else 'N\A'
        # physio = plan['benefits'][153]['variable'] if 153 in plan['benefits'] else 'N/A'
        # print_text = plan['name'] + '\t' + str(plan['price']) + '\t' +\
        #              consultant + '\t' + gp + '\t' + physio + '\t'
        # print_text = print_text.replace('\n', '')
        # print(print_text)
        # print(plan)
        plans.append(plan)

    data_frame = pandas.DataFrame(plans)

    # print(data_frame.head())
    print(data_frame.describe())
    # data_frame.to_csv('/Users/fpena/Projects/hia/data/processed_plans.csv', sep='\t', encoding='utf-8')


def files_in_folder(folder_path):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(folder_path):
        file_list.extend(filenames)

    return file_list


# https://api.hia.ie/api/plans/342
# https://api.hia.ie/api/plans/343
# https://api.hia.ie/api/plans/410
# https://api.hia.ie/api/plans/432
# https://api.hia.ie/api/plans/447
# https://api.hia.ie/api/plans/448
# https://api.hia.ie/api/plans/507
# https://api.hia.ie/api/plans/511
# https://api.hia.ie/api/plans/512
# https://api.hia.ie/api/plans/513
# https://api.hia.ie/api/plans/520
# https://api.hia.ie/api/plans/521
# https://api.hia.ie/api/plans/522
# https://api.hia.ie/api/plans/537
# https://api.hia.ie/api/plans/766
# https://api.hia.ie/api/plans/771
# https://api.hia.ie/api/plans/813
#
#
#
#



def main():
    json_file = DATA_FOLDER + 'prices/vhi_pmi_39_14_price.json'
    # process_plan(json_file)
    # load_benefits()
    # files_in_folder(DATA_FOLDER + 'prices/')
    # load_all_benefits()
    download_plans()


start = time.time()
main()
end = time.time()
total_time = end - start
print("%s: Total time = %f seconds" % (time.strftime("%Y/%m/%d-%H:%M:%S"), total_time))
