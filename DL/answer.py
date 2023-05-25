from datetime import datetime, timedelta


blue = 0
red = 0


def funk(road, lens=1, interval_hours=2):
    global blue, red
    for i_ in range(len(road[-1])):
        if road[i_][2] > road[i_ + lens][2] - timedelta(hours=interval_hours):
            # print(road[i], road[i+1])
            # print(f'{road[i_][0]} - {road[i_][3]} VS {road[i_ + lens][0]} - {road[i_ + lens][3]}')
            # print(f'{road[i_][2]} - {road[i_ + lens][2]}')
            if road[i_][3] > road[i_ + lens][3]:
                # print(road[i_][1])
                if road[i_][0] == 'синяя':
                    # print('blue')
                    blue += 1
                else:
                    # print('red')
                    red += 1
            elif road[i_][3] < road[i_ + lens][3]:
                if road[i_ + lens][0] == 'синяя':
                    # print('blue')
                    blue += 1
                else:
                    # print('red')
                    red += 1
            try:
                lens += 1
                funk(road, lens)
            except:
                lens = 1
    return [blue, red]


with open('1.txt', 'r', encoding='utf-8') as tabs:
    all_road = []
    for i in tabs:
        all_road.append((''.join(i.split('\n'))).split('\t'))

road_1 = []
road_2 = []
road_3 = []
for i in all_road:
    i[4] = int(i[4])
    i[3] = float(i[3].replace(',', '.').replace(' ', ''))
    i[2] = datetime(int(i[2][:4]), int(i[2][5:7]), int(i[2][8:10]),
                    int(i[2][11:13]), int(i[2][14:16]), int(i[2][17:19]))

    if i[4] == 20:
        road_3.append(i)
    elif i[4] == 16:
        road_2.append(i)
    else:
        road_1.append(i)

# print(road_1)
# print(road_2)
# print(road_3)

print('ROAD 1:')
red = 0
blue = 0
road_1_result = funk(road_1)
print(f'BLUE = {road_1_result[0]}, RED = {road_1_result[1]}')
print('\nROAD 2:')
red = 0
blue = 0
road_2_result = funk(road_2)
print(f'BLUE = {road_2_result[0]}, RED = {road_2_result[1]}')
print('\nROAD 3:')
red = 0
blue = 0
road_3_result = funk(road_3)
print(f'BLUE = {road_3_result[0]}, RED = {road_3_result[1]}')
print(f'\n\nTOTAL ON ALL ROADS:\n'
      f'BLUE = {road_1_result[0]+road_2_result[0]+road_3_result[0]}, '
      f'RED = {road_1_result[1]+road_2_result[1]+road_3_result[1]}')

