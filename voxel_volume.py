import numpy as np
import scipy.io as sio
import os


def open_mat(image: str) -> dict:
    """
    Открываем mat файл для прочтения маски и исходного изображения
    :param image: Путь к файлу с росширением .mat
    :return: Словарь со всеми данными .mat файла
    """
    test = sio.loadmat(image)
    return test


def find_mask(mask_dict: dict) -> list:
    """
    Получаем количество значений равных 1 и высчитываем площадь хрящей на срезе
    :param mask_dict: Словарь со всеми данными .mat файла
    :return: Площадь хрящей на срезе
    """
    mask = np.array(mask_dict['mask'], dtype=np.int8)
    array_mask = np.where(mask == 1)
    list_oxy_coord = [i for i in array_mask]
    return list_oxy_coord


def wrist_slice_volume(voxel_sz: float, list_coord) -> float:
    """
    Подсчёт объёма хрящей на одном срезе
    :param voxel_sz: Объём одного вокселя
    :param list_coord: Список координат с вокселями, соответсвующими хрящам кисти
    :return: Объём на одном срезе
    """
    wrist_volume = len(list_coord[0]) * voxel_sz
    return wrist_volume


def read_mat_files(current_path: str) -> list:
    """
    Поиск в директории всех файлов с расширением .mat
    :param current_path:
    :return: Возвращаем список содержащий названия файлов с расширением .mat в директории
    """
    list_mat_files = []
    for directs, direct, files in os.walk(current_path):
        for file in files:
            if file.endswith(".mat"):
                list_mat_files.append(file)
    return list_mat_files


def count_wrist_volume(directory_path: str) -> float:
    """
    Подсчёт полного объёма сегментированной кисти
    :param directory_path: Путь к диретории с масками
    :return: Суммарный объём сегментированного хряща по всем срезам составляет
    """
    voxel_thickness = 0.5
    pixel_size = 0.507812 * 0.507812
    voxel_size = voxel_thickness * pixel_size
    volume_counter = 0
    print('Функция - count_wrist_volume')
    for file in read_mat_files(directory_path):
        list_coord = find_mask(open_mat(directory_path + file))
        # print(f"Объём хряща на срезе равен {wrist_slice_volume(voxel_size, list_coord)} мм^3")
        volume_counter += wrist_slice_volume(voxel_size, list_coord)
    print(f"Суммарный объём сегментированного хряща по всем срезам составляет: {volume_counter} мм^3")
    return volume_counter


def create_coord_list_of_list(coord_dict: dict, coord_z: int) -> list:
    """
    Генерируем список списков с координатами в трех плоскостях (x, y, z) для одного среза
    :param coord_dict: Словарь с координатами маски сегментированной кисти
    :param coord_z: Координата Z для выбранного среза (соответствует номеру среза)
    :return: список с координатами в трех плоскостях: [[x1, y1, z1], [x2, y2, z2] [x3, y3, z3]]
    """
    coord_list = []
    mask = np.array(coord_dict['mask'], dtype=np.int8)
    array_mask = np.where(mask == 1)
    for i in range(len(array_mask[0])):
        coord_list.append([array_mask[0][i]+1, array_mask[1][i]+1, coord_z])
    return coord_list


def generator_mat_reader(current_path: str) -> list:
    """
    Генерируем список списков для всех срезов
    :param current_path: путь к директории
    :return: Список списков с координатами для всех срезов
    """
    global_list = []
    for directs, direct, files in os.walk(current_path):
        for file in files:
            if file.endswith(".mat"):
                slice = file.split('-')
                strip_slice = slice[2].rstrip('_edit.mat')
                list_ = create_coord_list_of_list(open_mat('/home/lg/ITMO/003/'+file), int(strip_slice))
                for i in list_:
                    global_list.append(i)
    return global_list


def compare_dimension(coronal_list: list, axial_list: list) -> tuple:
    """
    Проводим сравнение списков с координатами для коронарной плоскости и для аксиальной плоскости
    :param coronal_list: Список с координатами для корональной плоскости
    :param axial_list: Список с координатами для аксиальной плоскости
    :return: Возвращаем количество пикселей, находящихся в корональной плоскости, но отсутствующих в аксиальной, и
    наоборот...
    """
    counter_not_in_axial = 0
    counter_not_in_coronal = 0
    for cl in coronal_list:
        print(cl)
        if cl not in axial_list:
            counter_not_in_coronal += 1
    for axl in axial_list:
        if axl not in coronal_list:
            counter_not_in_axial += 1

    print(counter_not_in_axial, counter_not_in_coronal)
    return counter_not_in_coronal, counter_not_in_axial


if __name__ == '__main__':
    count_wrist_volume('/home/lg/ITMO/003/')
    coronal_list = generator_mat_reader('/home/lg/ITMO/003/')


    # print("Функция - print(find_mask)")
    # print(find_mask(open_mat('/home/lg/ITMO/003/IMG-0003-00063_edit.mat')))
    # create_coord_list_of_list(open_mat('/home/lg/ITMO/003/IMG-0003-00063_edit.mat'))
