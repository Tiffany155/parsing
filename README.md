### Оглавление

1. Описание проекта
2. Парсинг данных
3. Очистка данных
4. Предобработка данных
5. Хранение данных
6. Анализ данных и визуализация
7. Презентация результатов

### 1. Описание проекта

**Тема:** "Анализ типовых меню школ России"
 
 Питание в школе составляет более 50% ежедневного рациона ребёнка, оценка качества и эффективности школьного питания является актуальным направлением. Задачи в рамках предмета: оценить качество данных предоставляемых школами, проверить метрики на  соответствие СанПин, сбалансированность по БЖУ. В дальнейшем полученные данные планируется использовать с целью анализа влияния режима питания на физическое развитие, успеваемость и заболеваемость ЖКТ у школьников.

**Домен:** здравоохранение

**Проблема:** несмотря на наличие единой базы со школьными рационами, нет контроля по её заполнению. Рационы имеют типовой характер и составляются из наиболее доступных продуктов без учёта особенностей онтогенеза детей школьного возраста. Как следствие несбалансированный школьный рацион приводит к появлению проблем со здоровьем.


### 2. Парсинг данных

Сбор данных осуществлялся с сайта https://мониторингпитание.рф/данные/
Использовалась библиотека Selenium для парсинга страницы каждой школы каждого региона. Для ускорения сбора информации запускали 4 процесса с помощью модуля multiprocessing, в ручную задавая диапазон регионов для каждого процесса - это было обусловлено необходимостью прерывать работу парсера в связи с долгим процессом сбора информации и необходимостью останавливать работу парсера. Данные записывались в csv-файл.
Интересующие данные были записаны в следующие колонки:
- Регион: регион, в котором находится учебное учреждение;
- Учебное учреждение: наименование учебного учреждения;
- Доля несъедаемых: доля несьеденных порций от их исходного количества;
- Всего меню: количество выгруженных учебным учреждением школьных меню за 7 дней;
- % по Санпин: процент меню от числа выгруженных, соответствующих нормам СанПиН согласно подсчётам самого сайта;
- Стоимость завтрак: средняя стоимость порций завтрака за 7 дней;
- Стоимость обед: средняя стоимость порций обеда за 7 дней;
- Бз, Жз, Уз: средние значения белков, жиров и углеводов в порциях завтрака за 7 дней;
- Бо, Жо, Уо: средние значения белков, жиров и углеводов в порциях обеда за 7 дней;


### 3. Очистка данных

Первичную обработку данных проводили с использованием библиотеки pandas.

**1. Удаление дубликатов.**
   В ходе парсинга была замечено, что при отсуствии пропусков в строке данные могли дублироваться внутри региона, поэтому 
с помощью метода drop_duplicates() были удалены повторы в столбцах БЖУ(обед и ужин).

**2. Удаление пропусков.**
   - Были удалены строки, где на долю "всего меню" приходилось менее 50%.
   - Так как парсер был написан таким образом, чтобы не записывать строки со всеми отсуствующими значениями, вручную проверили наличие и удалили строки,где заполнено менее 50% числовых значений
     
 **3. Восстановление пропущенных значений.**
    В оставшихся стобцах на долю пропусков приходится менее 50%, поэтому было решено восстановить значения с помощью метода k ближайших соседей. Исключение составил столбец "Стоимость обеда" - там пропущено 53% значений, но так как в дальнейшем параметр стоимости не будет учитываться в анализе, было решено его также заполнить.
    
 **4. Работа с выбросами.**
    Для обнаружения выбросов использовали метод интерквартильных расстояний, данные значения заменялись на NaN. Далее значения заполнялись с помощью метода k ближайших соседей.


### 4. Предобработка данных

Значения в столбцах 'Бз','Жз','Уз','Бо','Жо','Уо' были переопределены в категориальные признаки "норма", "недостаток", "избыток" и записаны в соотвествующие столбцы 'proteins_b','fats_b','carb_b' и 'proteins_d','fats_d','carb_d'. В столбцах 'breakf' и 'lunch' записывали 1,если по всем трём столбцах категориальный признак соотвествовал значению "норма", во всех остальных случаях записывали 0.


### 5. Хранение данных
Для хранения данных была выбрана СУБД SQLite. Данные из csv-файла были перенесены в базу посредством скрипта, использующего встроенный модуль sqlite.


### 6. Анализ данных и визуализация
С помощью Power BI построили дашборд, на котором отразили основным метрики.

В качестве метрик были выбраны:
1) Доля меню соответствующих Санпин: это наиболее важный показатель безопасности пищевых продуктов и соответствия требованиям.
2) Средняя стоимость завтрака/обеда: краткий обзор средней стоимости завтрака/обеда для мониторинга.
3) Сбалансированность меню по БЖУ завтрак/обед: в соответсвии с рекомендациями ВОЗ и методическими рекомендациями МР формула сбалансированного питания - 1:1:4. Продолжительное отклонение рациона от нормы ведёт к проблемам со здоровьем.
4) Отклонение содержания нутриентов от нормы завтрак/обед: в этот параметр входит как избыток, так и недостаток по каждому нутриенту. Совместно с 5 показатель можно наглядно увидеть, в какую стороны приходится дисбаланс.
5) Наиболее дефицитный нутриент завтрак/обед: важный показатель, на основании которого можно дать рекмендации по улучшению рациона

### 7. Презентация результатов
Подготовили итоговую презентацию результатов проекта.


