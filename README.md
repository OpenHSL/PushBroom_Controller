# PushBroom_Controller

Программное обеспечение для управления процессом съёмки щелевого гиперспектрометра. Данная версия программы предназначения для работы с гиперспектральным микроскопом.
Конечный пользователь может расширить сферу применения данного ПО для любых щелевых гиперспектрометров, оборудованных шаговым механизмом при доработке модулей, реализующих API камеры и шагового механизма,  с учётом API реализованного здесь.

## Минимальные технические требования
- Микрокомпьютер Raspberry Pi4
- Щелевой гиперспектрометр на базе сенсора Basler 
- ОС: RaspOS
- Python 3.9 или старше

## Запуск программы

Для запуска ПО в режиме CLI необходимо указать требуемые параметры в файле 
 ##### settings.py

После чего выполнить команду:

##### python main.py

Для запуска ПО в режиме GUI необходимо выполнить команду:

#### python micro_app.py

## Примеры полученных и сформированных данных:

Следующие наборы даных обработаны и сформированы с помощью [OpenHSL](https://github.com/OpenHSL/OpenHSL)

1) [Неокрашенный микропрепарат](https://www.kaggle.com/datasets/openhsl/hyperdataset-unstained-tissue-microslide)
2) [Окрашенный микропрепарат](https://www.kaggle.com/datasets/openhsl/hyperdataset-stained-microscope)
3) [Растительный микропрепарат](https://www.kaggle.com/datasets/openhsl/hyperdata-plant-microscope) 
