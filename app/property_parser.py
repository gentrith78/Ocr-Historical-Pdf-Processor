import re
from typing import List, Tuple

import pandas as pd

try:
    from .structured_data import Comparison_Instance, known_columns, Property, state_names, WordData
    from .utils import similarity
    from .utils import rmv_bad_chars
except:
    from structured_data import Comparison_Instance, known_columns, Property, state_names, WordData
    from utils import similarity
    from utils import rmv_bad_chars


class NumeEntitiesParser():
    """
    - Get all columns and their coordinates

    """

    def __init__(self, lines: List[List[WordData]]):
        self.WithinRangeThreshold = 21
        self.OutsideRangeThreshold = 40
        self.lines: List[List[WordData]] = lines
        self.columns = [WordData(text='Control', TL=(1635, 768), TR=(1633, 665)), WordData(text='Service',
                                                                                           TL=(1694, 768),
                                                                                           TR=(1694, 671)),
                        WordData(text='Stay', TL=(1755, 769), TR=(1757, 709)),
                        WordData(text='Beds', TL=(1834, 768), TR=(1835, 704)),
                        WordData(text='Admissions', TL=(1936, 769),
                                 TR=(1935, 619)), WordData(text='Census', TL=(2044, 772), TR=(2045, 680)),
                        WordData(text='Bassinets',
                                 TL=(2128, 771), TR=(2125, 653)),
                        WordData(text='Births', TL=(2213, 773), TR=(2213, 697)),
                        WordData(text='Newborn Census', TL=(2287, 771), TR=(2286, 652)), WordData(text='Total',
                                                                                                  TL=(2393, 773),
                                                                                                  TR=(2392, 702))]

    def __get_columns(self, lines):
        for line in lines:
            merged_line = ' '.join(el.text for el in line)
            if merged_line.startswith('Control'):
                pass
            founded_cols = []
            should_i_skip = False
            if len(merged_line.split(' ')) < 5:
                continue
            for ind, piece in enumerate(line):
                if piece.text.isspace() or piece.text == '' or should_i_skip:
                    should_i_skip = False
                    continue
                if 'Newborn' in piece.text and 'Census' in line[ind + 1].text:
                    should_i_skip = True
                    piece.text = 'Newborn Census'
                    founded_cols.append(piece)
                    continue
                for col in known_columns:
                    if similarity(piece.text, col) > 0.7:
                        founded_cols.append(piece)
                        break
                if len(founded_cols) <= len(known_columns):
                    if len(known_columns) - len(founded_cols) < 4:
                        return founded_cols

    def get_num_entities(self, num_columns: List[WordData]) -> List[Comparison_Instance]:
        numerical_columns: List[Comparison_Instance] = []
        for value in num_columns:
            comparison = []
            for name in self.columns:
                if value.TL[0] >= name.TR[0]:
                    substract_value = value.TL[0] - name.TL[0]
                else:
                    substract_value = name.TL[0] - value.TL[0]
                compare_obj = Comparison_Instance(
                    column_value=value.text,
                    column_name=name.text,
                    substract_value=substract_value
                )
                comparison.append(compare_obj)
            numerical_column = min(comparison, key=lambda x: x.substract_value)
            if numerical_column.substract_value < 150:
                numerical_columns.append(numerical_column)
        return numerical_columns

    def get_num_entities2(self, num_columns) -> List[Comparison_Instance]:
        num_entities: List[Comparison_Instance] = []
        classification_codes, inpatient_data, newborn_data, expenses = self._get_dataTypesColumnRange()

        #
        num_entities.extend(self._get_clasification_codesCols(classification_codes, num_columns))  # DONE
        #
        num_entities.extend(self._get_inpatient_dataCols(inpatient_data, num_columns))
        #
        num_entities.extend(self._get_newborn_dataCols(newborn_data, num_columns))
        #
        num_entities.extend(self._get_expensesCols(expenses, num_columns))

        return num_entities

    def _get_clasification_codesCols(self, clasification_codes, num_cols: List[WordData]) \
            -> List[Comparison_Instance]:
        clasification_codes_cols: List[Comparison_Instance] = []

        control = Comparison_Instance(
            column_value='',
            column_name='Control',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )
        service = Comparison_Instance(
            column_value='',
            column_name='Service',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )
        stay = Comparison_Instance(
            column_value='',
            column_name='Stay',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )

        control = self._left_col(control, num_cols, clasification_codes)
        service = self._middle_col(service, num_cols, clasification_codes)
        stay = self._right_col(stay, num_cols, clasification_codes)

        clasification_codes_cols.append(control)
        clasification_codes_cols.append(service)
        clasification_codes_cols.append(stay)

        return clasification_codes_cols

    def _get_inpatient_dataCols(self, inpatient_data, num_cols: List[WordData]) \
            -> List[Comparison_Instance]:
        inpatient_data_cols: List[Comparison_Instance] = []

        beds = Comparison_Instance(
            column_value='',
            column_name='Beds',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )
        admissions = Comparison_Instance(
            column_value='',
            column_name='Admissions',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )

        census = Comparison_Instance(
            column_value='',
            column_name='Census',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )

        beds = self._left_col(beds, num_cols, inpatient_data)
        admissions = self._middle_col(admissions, num_cols, inpatient_data)
        census = self._right_col(census, num_cols, inpatient_data)

        inpatient_data_cols.append(beds)
        inpatient_data_cols.append(admissions)
        inpatient_data_cols.append(census)

        return inpatient_data_cols

    def _get_newborn_dataCols(self, newborn_data, num_cols: List[WordData]) \
            -> List[Comparison_Instance]:
        newborn_data_cols: List[Comparison_Instance] = []

        bassinites = Comparison_Instance(
            column_value='',
            column_name='Bassinets',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )
        births = Comparison_Instance(
            column_value='',
            column_name='Births',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )

        newborn_census = Comparison_Instance(
            column_value='',
            column_name='Newborn Census',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )

        bassinites = self._left_col(bassinites, num_cols, newborn_data)
        births = self._middle_col(births, num_cols, newborn_data)
        newborn_census = self._right_col(newborn_census, num_cols, newborn_data)

        newborn_data_cols.append(bassinites)
        newborn_data_cols.append(births)
        newborn_data_cols.append(newborn_census)

        return newborn_data_cols

    def _get_expensesCols(self, expenses, num_cols: List[WordData]) \
            -> List[Comparison_Instance]:
        newborn_data_cols: List[Comparison_Instance] = []

        total = Comparison_Instance(
            column_value='',
            column_name='Total',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )
        payroll = Comparison_Instance(
            column_value='',
            column_name='Payroll',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )
        personnel = Comparison_Instance(
            column_value='',
            column_name='Personnel',
            substract_value=0  # we use Top left x coord in order to sort by x coord
        )

        # filter cols
        filtered_cols: List[WordData] = []
        for c in num_cols:
            if c.text.strip().isdigit():
                filtered_cols.append(c)
            else:
                if len(c.text) > 1:
                    if c.text[1::].isdigit():
                        filtered_cols.append(c)

        num_cols = filtered_cols

        total = self._left_col(total, num_cols, expenses)
        payroll = self._middle_col(payroll, num_cols, expenses)
        personnel = self._right_col(personnel, num_cols, expenses)

        # get personel
        for w in num_cols:
            if abs(w.TL[0] - expenses[1]) > 20 and w.TL[0] > expenses[1]:  # the right most side col
                personnel = Comparison_Instance(
                    column_value=w.text,
                    column_name='Personnel',
                    substract_value=w.TL[0]  # we use Top left x coord in order to sort by x coord
                )

        newborn_data_cols.append(total)
        newborn_data_cols.append(payroll)
        newborn_data_cols.append(personnel)

        return newborn_data_cols

    def _get_dataTypesColumnRange(self) -> Tuple:
        clasification_codes: List[int, int] = []
        inpatient_data: List[int, int] = []
        newborn_data: List[int, int] = []
        expenses: List[int, int] = []
        for l in self.lines:
            m = ' '.join(el.text for el in l)
            for indW, w in enumerate(l):
                if similarity('fication', w.text) > 0.8:
                    start_coord = w.TL[0]
                    end_coord = w.TR[0]
                    clasification_codes = [start_coord, end_coord]
                if similarity('Inpatient', w.text) > 0.8 and similarity('Data', l[indW + 1].text) > 0.8:
                    start_coord = w.TL[0]
                    end_coord = l[indW + 1].TR[0]
                    inpatient_data = [start_coord, end_coord]
                if similarity('Newborn', w.text) > 0.8 and similarity('Data', l[indW + 1].text) > 0.8:
                    start_coord = w.TL[0]
                    end_coord = l[indW + 1].TR[0]
                    newborn_data = [start_coord, end_coord]
                if similarity('thausands', w.text) > 0.8:
                    start_coord = w.TL[0]
                    end_coord = w.TR[0]
                    expenses = [start_coord, end_coord]

        return clasification_codes, inpatient_data, newborn_data, expenses

    def _left_col(self, column_entity: Comparison_Instance, words: List[WordData], range) -> Comparison_Instance:
        edited_column = column_entity
        candidates: List[Comparison_Instance] = []

        threshold = self.__side_thresholds(mode=1)

        for word in words:
            if abs(word.TL[0] - range[0]) > 100:
                continue
            candidate = Comparison_Instance(
                column_value=word.text,
                column_name=column_entity.column_name,
                substract_value=abs(word.TL[0] - (range[0] - threshold))
            )
            candidates.append(candidate)

        if candidates:
            return min(candidates, key=lambda x: x.substract_value)

        return edited_column

    def _middle_col(self, column_entity: Comparison_Instance, words: List[WordData], range) -> Comparison_Instance:
        edited_column = column_entity
        candidates: List[Comparison_Instance] = []

        mid_of_range = (range[0] + range[1]) / 2

        for word in words:
            if abs(word.TL[0] - mid_of_range) > 100:
                continue
            candidate = Comparison_Instance(
                column_value=word.text,
                column_name=column_entity.column_name,
                substract_value=abs(word.TL[0] - mid_of_range)
            )
            candidates.append(candidate)

        if candidates:
            return min(candidates, key=lambda x: x.substract_value)

        return edited_column

    def _right_col(self, column_entity: Comparison_Instance, words: List[WordData], range) -> Comparison_Instance:
        edited_column = column_entity
        candidates: List[Comparison_Instance] = []

        threshold = self.__side_thresholds(mode=3)

        for word in words:
            if abs(word.TL[0] - range[1]) > 100:
                continue
            candidate = Comparison_Instance(
                column_value=word.text,
                column_name=column_entity.column_name,
                substract_value=abs(word.TL[0] - (range[1] - threshold))
            )
            candidates.append(candidate)

        if candidates:
            return min(candidates, key=lambda x: x.substract_value)

        return edited_column

    def __is_within_range(self, word: WordData, range) -> bool:
        if range[0] < word.TL[0] < range[1]:
            return True
        return False

    def __get_left_column(self, word: WordData, range, mode: int = 1) -> bool:
        withing_range_threshold, outside_range_threshold, right_side_threshold = self.__thresholds(mode)

        if self.__is_within_range(word, range):
            # lower threshold
            if abs(word.TL[0] - range[0]) <= withing_range_threshold:
                return True
            else:
                return False
        else:
            # higher threshold
            if abs(word.TL[0] - range[0]) <= outside_range_threshold:
                return True
            else:
                return False

    def __get_right_column(self, word: WordData, range, mode: int = 1) -> bool:
        withing_range_threshold, outside_range_threshold, right_side_threshold = self.__thresholds(mode)

        if self.__is_within_range(word, range):
            # lower threshold
            if abs(word.TL[0] - range[1]) <= right_side_threshold:
                return True
            else:
                return False
        else:
            # higher threshold
            if abs(word.TL[0] - range[1]) <= outside_range_threshold:
                return True
            else:
                return False

    def __get_middle_column(self, word: WordData, range, mode: int = 1) -> bool:
        withing_range_threshold, outside_range_threshold, right_side_threshold = self.__thresholds(mode)

        if self.__is_within_range(word, range):
            range[0] = range[0] + withing_range_threshold
            range[1] = range[1] - right_side_threshold
            if range[0] < word.TL[0] < range[1]:
                return True
        return False

    def __side_thresholds(self, mode):
        if mode == 1:  # left
            threshold = 20
        if mode == 2:  # middle
            threshold = 10
        if mode == 3:  # right
            threshold = 20

        return threshold

    def __thresholds(self, mode):

        if mode == 1:
            withing_range_threshold = 15
            outside_range_threshold = 45
            right_side_threshold = 10
        if mode == 2:
            withing_range_threshold = 15
            outside_range_threshold = 40
            right_side_threshold = 10
        if mode == 3:
            withing_range_threshold = 15
            outside_range_threshold = 40
            right_side_threshold = 10
        if mode == 4:
            withing_range_threshold = 65
            outside_range_threshold = 25
            right_side_threshold = 10

        return withing_range_threshold, outside_range_threshold, right_side_threshold


class PropertyParser(NumeEntitiesParser):
    def __init__(self, lines, page_nr):
        NumeEntitiesParser.__init__(self, lines)
        self.lines = lines
        self.page_nr = page_nr
        self.state = self._get_state()
        self.parcels = []

    def process(self):
        items_list = self._get_items()
        for item in items_list:
            if len(item) > 1:
                parcel = self._get_fields(item)
                self.parcels.append(parcel)
            else:
                print('small item')
                print(item)

    def _get_fields(self, item):
        item, num_cols = self._split_data(item)
        num_entities: List[Comparison_Instance] = self.get_num_entities2(num_cols)
        STAR = self._hasStar(item)
        STATE = self.state
        CITY, COUNTY = self._city_county(item)
        NAME = self._name(item, CITY, COUNTY)
        EST = self._est(item, CITY, COUNTY)
        TEL = self._tel(item, CITY, COUNTY)
        ADDRESS = self._address(item, CITY, COUNTY, str(EST))
        ADM, FACILITY = self._adm_facility(item)
        parcel_obj = Property(
            page=self.page_nr,
            star=STAR,
            state=STATE,
            conty=COUNTY,
            city=CITY,
            name=NAME,
            est=EST,
            tel=TEL,
            address=ADDRESS,
            adm=ADM,
            facility=FACILITY,
        )
        return self.serialise_numerical_data(num_entities, parcel_obj)

    def serialise_numerical_data(self, num_cols, parcel_obj):
        for l in num_cols:
            if l.column_name == 'Control':
                parcel_obj.ownership_control = l.column_value
            if l.column_name == 'Service':
                parcel_obj.service_type = l.column_value
            if l.column_name == 'Stay':
                parcel_obj.length_stay = l.column_value
            if l.column_name == 'Beds':
                parcel_obj.beds = l.column_value
            if l.column_name == 'Admissions':
                parcel_obj.admissions = l.column_value
            if l.column_name == 'Census':
                parcel_obj.avg_daily_census = l.column_value
            if l.column_name == 'Bassinets':
                parcel_obj.bassinets = l.column_value
            if l.column_name == 'Births':
                parcel_obj.births = l.column_value
            if l.column_name == 'Newborn Census':
                parcel_obj.newborn_census = l.column_value
            if l.column_name == 'Total':
                parcel_obj.tot_exp = l.column_value
            if l.column_name == 'Payroll':
                parcel_obj.payroll = l.column_value
            if l.column_name == 'Personnel':
                parcel_obj.paid_person = l.column_value
        return parcel_obj

    def _hasStar(self, item):
        first_line = ' '.join(el.text for el in item[0])
        second_line = ' '.join(el.text for el in item[1])
        if 'County' in first_line or 'Division' in first_line:
            if re.search(r'^\w', second_line.strip()[0]) == None and not second_line.strip().isdigit():
                return 'Yes'
        else:
            if re.search(r'^\w', first_line.strip()[0]) == None and not first_line.strip().isdigit():
                return 'Yes'
        return 'No'

    def _city_county(self, item):
        merged_first_line = ' '.join(el.text for el in item[0])
        if merged_first_line.strip().endswith('County') \
                or 'Division' in merged_first_line.strip():
            if len(merged_first_line.split('-')) > 1:
                return ' '.join(merged_first_line.split('-')[0:-1]), merged_first_line.split('-')[-1]
            if re.search('([A-Z]+\W)+', merged_first_line) != None:
                return re.search('([A-Z]+\W)+', merged_first_line).group(), ''
        return '', ''

    def _name(self, item, city, county):
        if city == '' and county == '':
            complete_line = ' '.join(el.text for el in item[0])
            if re.search(r'([A-Z]+\W+)+', complete_line) != None:
                return re.search(r'([A-Z]+\W+)+', complete_line).group()
        else:
            complete_line = ' '.join(el.text for el in item[1])
            if re.search(r'([A-Z]+\W+)+', complete_line) != None:
                return re.search(r'([A-Z]+\W+)+', complete_line).group()
        return ''

    def _est(self, item, city, county):
        if city == '' and county == '':
            complete_line = ' '.join(el.text for el in item[0])
            complete_line = complete_line + ' '.join(el.text for el in item[1])
        else:
            complete_line = ' '.join(el.text for el in item[1])
            complete_line = complete_line + ' '.join(el.text for el in item[2])
        if 'Est' in complete_line:
            if re.search('^\d+', complete_line.split('Est')[1].strip()) != None:
                est = re.search('^\d+', complete_line.split('Est')[1].strip()).group()
                if est.strip().isdigit():
                    return int(est)

    def _tel(self, item, city, county):

        if city == '' and county == '':
            complete_line = ' '.join(el.text for el in item[0])
            complete_line = complete_line + ' '.join(el.text for el in item[1])
        else:
            complete_line = ' '.join(el.text for el in item[1])
            complete_line = complete_line + ' '.join(el.text for el in item[2])
        if complete_line.find(' Tel ') != -1:
            start_letter = complete_line.find(' Tel') + 4
            if not complete_line[start_letter::].find(', ', 1) in [0, -1] or not complete_line[start_letter::] \
                                                                                         .find(',Adm', 1) in [0, -1]:
                end_letter = complete_line[start_letter::].find(', ', 1)
                return complete_line[start_letter::][0:end_letter].replace('..', '').replace('â€¦', '')
            if not complete_line[start_letter::].find('..', 1) in [0, -1]:
                end_letter = complete_line[start_letter::].find('..', 1)
                return complete_line[start_letter::][0:end_letter].replace('..', '').replace('â€¦', '')
            if not complete_line[start_letter::].find(' Adm', 1) in [0, -1]:
                end_letter = complete_line[start_letter::].find('..', 1)
                return complete_line[start_letter::][0:end_letter].replace('..', '').replace('â€¦', '')
        if complete_line.find(' Tal ') != -1:
            start_letter = complete_line.find(' Tal') + 4
            if not complete_line[start_letter::].find(', ', 1) in [0, -1]:
                end_letter = complete_line[start_letter::].find(', ', 1)
                return complete_line[start_letter::][0:end_letter].replace('..', '').replace('â€¦', '')
            if not complete_line[start_letter::].find('..', 1) in [0, -1]:
                end_letter = complete_line[start_letter::].find('..', 1)
                return complete_line[start_letter::][0:end_letter].replace('..', '').replace('â€¦', '')
            if not complete_line[start_letter::].find(' Adm', 1) in [0, -1]:
                end_letter = complete_line[start_letter::].find('..', 1)
                return complete_line[start_letter::][0:end_letter].replace('..', '').replace('â€¦', '')
        return ''

    def _address(self, item, city, county, est):
        if est == '':
            return ''

        if city == '' and county == '':
            complete_line = ' '.join(el.text for el in item[0])
            complete_line = complete_line + ' '.join(el.text for el in item[1])
        else:
            complete_line = ' '.join(el.text for el in item[1])
            complete_line = complete_line + ' '.join(el.text for el in item[2])
        start_of_address = complete_line.find(est) + len(est)
        splitted_line = complete_line[start_of_address::].strip().split(' ')
        for ind, l in enumerate(splitted_line):
            if '-' in l or '–' in l:
                if len(l.replace(' ', '').strip()) > 1:
                    merged_address = l.replace('-', '') + ' '
                else:
                    merged_address = ''
                for el in splitted_line[ind + 1::]:
                    if '-' in el or ' Tal' in el or ' Tel' in el:
                        break
                    else:
                        merged_address += f"{el} "
                return merged_address

    def _adm_facility(self, item):
        adm = ''
        facility = ''
        for l in item:
            merged_line = ''.join(el.text for el in l)
            if re.search('F\W+\d+(\W+\d+){2,}', merged_line) != None:
                facility = re.search('F\W+\d+(\W+\d+){2,}', merged_line).group().replace(' ', '')
            if re.search('A\W+\d+((\W+\d+)+)?', merged_line) != None:
                adm = re.search('A\W+\d+((\W+\d+)+)?', merged_line).group().replace(' ', '')

        return adm, facility

    def _get_state(self):
        for l in self.lines:
            merged_line = ' '.join(el.text for el in l)
            if len(l) < 4:
                for s in state_names:
                    if s.lower() in merged_line.lower():
                        return s

    def _split_data(self, item) -> Tuple[List[WordData], List[WordData]]:
        "will split num entities from word entities"
        first_line = ' '.join(el.text for el in item[0])
        same_col: List[WordData] = []
        num_cols: List[WordData] = []
        thershold = 60

        if 'County' in first_line or 'Division' in first_line:
            first_line = item[1]
            ind_of_first_line = 1

        else:
            first_line = item[0]
            ind_of_first_line = 0

        for ind, el in enumerate(first_line):
            if el == first_line[-1]:
                break
            if '..' in el.text or ' Adm' in el.text:
                same_col.append(rmv_bad_chars(el))
                num_cols = first_line[ind + 1::]
                break
            if (first_line[ind + 1].TL[0] - el.TR[0]) < thershold:
                same_col.append(rmv_bad_chars(el))
            else:
                same_col.append(rmv_bad_chars(el))
                num_cols = first_line[ind + 1::]
                break

        item[ind_of_first_line] = same_col

        return item, num_cols

    def _get_items(self):
        items = []
        start_indexes = []
        for ind, line in enumerate(self.lines):
            complete_line = ' '.join(el.text for el in line)
            if re.search('([A-Z]{2,}\s){2,}', complete_line[2::].replace('-', '').replace("'", '')) and \
                    (' Est ' in complete_line or ' Tel ' in complete_line
                     or ' Tal ' in complete_line):
                if ' '.join(el.text for el in self.lines[ind - 1]).strip().endswith('County') \
                        or 'Division' in ' '.join(el.text for el in self.lines[ind - 1]).strip():
                    start_indexes.append(ind - 1)
                else:
                    start_indexes.append(ind)

        for ind_ind, el in enumerate(start_indexes):
            if el != start_indexes[-1]:
                item = self.lines[el:start_indexes[ind_ind + 1]]
                items.append(item)
            else:
                item = self.lines[el:-1]
                items.append(item)

        return items
