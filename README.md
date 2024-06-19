# PushBroom_Controller

Программное обеспечение для управления процессом съёмки щелевого гиперспектрометра. Данная версия программы предназначения для работы с гиперспектральным микроскопом на базе микрокомпьюетра Raspberry Pi4.
Конечный пользователь может расширить сферу применения данного ПО для любых щелевых гиперспектрометров, оборудованных шаговым механизмом при доработке модулей, реализующих API камеры и шагового механизма,  с учётом API реализованного здесь.

Перечень направлений применения данного ПО:
- Экологическая безопасность (определение болезней растений, индекса зелёной массы, влажности почвы, концентрации удобрений в почве);
- Пищевая безопасность;
- Сортировка отходов по различным материалам;
- Медицина (экспресс диагностика онкозаболеваний, патологий сердца и кровообращения, заболеваний сетчатки, мастэктомии, неинвазивная диагностика заболеваний кожи и т.д.);
- Промышленность (определение качества сырья и готовой продукции, определение пород и их химического состава);
- и т.д.

## Минимальные технические требования
- Микрокомпьютер Raspberry Pi4
- Щелевой гиперспектрометр на базе сенсора Basler 
- ОС: RaspOS
- Python 3.9 или старше

## Запуск программы

Для запуска ПО в режиме CLI необходимо указать требуемые параметры в файле *settings.py*:
- number_of_steps количество шагов для шагового механизма;
- exposure выдержка в мс (подбирается экспериментально, оценивая освещенность сцены);
- gain коэффициент усиления сигнала (подбирается экспериментально, оценивая освещенность сцены);
- direction направление движения шагового механизма (0 и 1 отвечают за прямое движение и обратное);
- path_to_save путь к папке сохранения;
- mode режим работы шагового механизма (0 или 1 отвечают за полный шаг или 1/2 шага).

После чего выполнить команду:

`python main.py`

Для запуска ПО в режиме GUI необходимо выполнить команду:

`python micro_app.py`

## Примеры полученных и сформированных данных:

Нижепредставленные наборы даных получены данным ПО, а в дальнейшем обработаны и сформированы с помощью платформы с открытым исходным кодом [OpenHSL](https://github.com/OpenHSL/OpenHSL)

1) [Неокрашенный микропрепарат](https://www.kaggle.com/datasets/openhsl/hyperdataset-unstained-tissue-microslide)
2) [Окрашенный микропрепарат](https://www.kaggle.com/datasets/openhsl/hyperdataset-stained-microscope)
3) [Растительный микропрепарат](https://www.kaggle.com/datasets/openhsl/hyperdata-plant-microscope) 
