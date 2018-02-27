import time
import math
import os
import urllib.request

import cv2

from celery import shared_task

from .models import Algorithm, ImageExample, History


def download_images(url, algorithm, image_type, size):
    time.sleep(1) # чтобы сервер не забанил

    print('start donwload')
    image_urls = urllib.request.urlopen(url).read().decode()

    path = 'media/algo_{0}/{1}'.format(algorithm.id, image_type)
    if not os.path.exists(path):
        os.makedirs(path)

    pic_num = 1
    for i in image_urls.split('\n')[:30]:
        try:
            image_path = "{0}/{1}.jpg".format(path, str(pic_num))
            urllib.request.urlretrieve(i, image_path)
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            resized_image = cv2.resize(img, size)
            cv2.imwrite(image_path, resized_image)
            # сохраняем image example instance
            image_example = ImageExample.objects.create(algorithm=algorithm, image_type=image_type)
            image_example.file.name = image_path[image_path.find('/media/') + 7:]
            image_example.save()
            pic_num += 1
        except Exception as e:
            print(str(e))
    print('execute downloading')
    return pic_num


@shared_task
def run_image_processing(algorithm_id, positive_url, negative_url):
    algorithm = Algorithm.objects.get(id=algorithm_id)
    if positive_url:
        download_images(positive_url, algorithm, 'positive', size=(50, 50))
    # num - количество negative картинок
    num = download_images(negative_url, algorithm, 'negative', size=(100, 100))

    # open cv обработка
    # Генерация текстовых файлов bg.txt и info.dat
    print('start OPEN CV')
    path = 'media/algo_{0}/'.format(algorithm.id)
    image_examples = ImageExample.objects.filter(algorithm_id=algorithm_id)
    for image_example in image_examples:
        print(image_example.file.name)
        fn = image_example.file.name
        fn = fn[fn[:fn.rfind('/')].rfind('/') + 1:]
        if image_example.image_type == 'negative':
            line = '{0}\n'.format(fn)
            with open(path + 'bg.txt', 'a') as f:
                f.write(line)
        elif image_example.image_type == 'positive':
            line = '{0} 1 0 0 50 50\n'.format(fn)
            with open(path + 'info.dat', 'a') as f:
                f.write(line)

    print('END OPEN CV')
    # создать папки data, info
    os.makedirs(path + 'data')
    os.makedirs(path + 'info')
    os.system('cd {path}info && touch info.lst'.format(path=path))

    time.sleep(3)
    print('Continue work')

    positive_images = ImageExample.objects.filter(algorithm_id=algorithm_id, image_type='positive')
    cnt = 0
    for img in positive_images:
        file_name = img.file.name[img.file.name.find('positive/'):]
        os.system('cd {path} && opencv_createsamples -img {file_name} -bg bg.txt -info info/info.lst -pngoutput info -maxxangle 0.5 -maxyangle -0.5 -maxzangle 0.5 -num {num}'
              .format(file_name=file_name, path=path, num=num))
        cnt += 1
        time.sleep(1)

    print('I"m DONE YPU HAVE 60 SECONDS for checking me')
    time.sleep(3)

    os.system('cd {path} && opencv_createsamples -info info/info.lst -num {num} -w 20 -h 20 -vec positives.vec'
              .format(path=path, num=num))

    num_pos = math.ceil(.8 * cnt * num)
    os.system('cd {path} && opencv_traincascade -data data -vec positives.vec -bg bg.txt -numPos {numPos} -numNeg {numNeg} -numStages {numStages} -w 20 -h 20'
              .format(path=path, numPos=num_pos, numNeg=num_pos//2, numStages=10))
    xml_path = '{}data/cascade.xml'.format(path)


    while True:
        if os.path.exists(xml_path):
            break
        time.sleep(5)

    print(xml_path)
    print('DONE')
    algorithm = Algorithm.objects.get(id=algorithm_id)

    xml_path = xml_path[xml_path.find('media/') + 6:]
    print(xml_path)
    algorithm.xml_file.name = xml_path
    algorithm.status = 'Done'
    algorithm.save()

    # удаление всех записей ImageExample with algorithm_id
    ImageExample.objects.filter(algorithm_id=algorithm.id).delete()

    os.system('cd {path} && rm -rf info')
    time.sleep(3)


@shared_task
def run_test_processing(history_ids):
    histories = History.objects.filter(pk__in=history_ids)
    for history in histories:
        xml_path = history.algorithm.xml_file.path
        haar_cascade = cv2.CascadeClassifier(xml_path)
        input_image_path = history.input_image.path
        img = cv2.imread(input_image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        haar = haar_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in haar:
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        path = input_image_path[:input_image_path.rfind('/')]
        print('history id ', history.id)
        output_filename = 'result_{}.jpg'.format(history.id)
        output_image_path = "".join([path, '/', output_filename])
        cv2.imwrite(output_image_path, img)
        cv2.destroyAllWindows()

        # update history model
        path = input_image_path[input_image_path.find('/media/') + 6:input_image_path.rfind('/')]
        output_image_path = "".join([path, '/', output_filename])

        history.output_image.name = output_image_path
        history.status = 'Done'
        history.save()
