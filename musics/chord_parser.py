import re
from typing import List

def text_from_chord_tone(chord_tone: List[bool]) -> str:
    third = None
    fifth = None
    sixth = None
    seventh = None
    tensions = []
    omits = []
    
    original = list(chord_tone)
    chord_tone[0] = False

    if chord_tone[1]:
        chord_tone[1] = False
        tensions.append('b9')

    # third
    if chord_tone[4]:
        chord_tone[4] = False
        third = 'Maj'

    if chord_tone[3]:
        chord_tone[3] = False
        if third is None:
            third = 'Min'
        else:
            tensions.append('#9')

    if chord_tone[5]:
        chord_tone[5] = False
        if third is None:
            third = 'Sus4'
        else:
            tensions.append('11')

    if chord_tone[2]:
        chord_tone[2] = False
        if third is None:
            third = 'Sus2'
        else:
            tensions.append('9')

    if third is None:
        omits.append('3')

    # fifth
    if chord_tone[7]:
        chord_tone[7] = False
        fifth = 'Perf'

    if chord_tone[6] and chord_tone[8]:
        chord_tone[6] = False
        chord_tone[8] = False
        if fifth is None:
            if third == 'Maj':
                third = None
                fifth = 'Aug'
                tensions.append('#11')
            elif third == 'Min':
                third = None
                fifth = 'Dim'
                tensions.append('b13')
        else:
            tensions.append('#11')
            tensions.append('b13')

    if chord_tone[6]:
        chord_tone[6] = False
        if fifth is None:
            if third == 'Min':
                third = None
                fifth = 'Dim'
            else:
                fifth = 'b5'
        else:
            tensions.append('#11')

    if chord_tone[8]:
        chord_tone[8] = False
        if fifth is None:
            if third == 'Maj':
                third = None
                fifth = 'Aug'
            else:
                fifth = '#5'
        else:
            tensions.append('b13')

    if fifth is None:
        omits.append('5')
    
    if chord_tone[11]:
        chord_tone[11] = False
        seventh = 'Maj'

    if chord_tone[10]:
        chord_tone[10] = False
        if seventh is None:
            if fifth == 'Dim':
                third = 'Min'
                fifth = 'b5'
            seventh = 'Min'
        else:
            raise Exception('ERROR: Chord must not contain both [m7] and [M7]')

    if chord_tone[9]:
        chord_tone[9] = False
        if seventh is None:
            if fifth == 'Dim':
                seventh = 'Dim'
            else:
                sixth = 'Maj'
        else:
            tensions.append('13')

    text = ''
    chord_tone[0] = True

    if third == 'Maj':
        chord_tone[4] = True
    elif third == 'Min':
        chord_tone[3] = True
        text += 'm'

    if fifth == 'Perf':
        chord_tone[7] = True
    elif fifth == 'Dim':
        chord_tone[3] = True
        chord_tone[6] = True
        text += 'dim'
    elif fifth == 'Aug':
        chord_tone[4] = True
        chord_tone[8] = True
        text += 'aug'

    if sixth == 'Maj':
        text += '6'
        chord_tone[9] = True

    if seventh == 'Dim':
        chord_tone[9] = True
        text += '7'
    elif seventh == 'Maj':
        chord_tone[11] = True
        text += 'M7'
    elif seventh == 'Min':
        chord_tone[10] = True
        text += '7'

    if fifth == 'b5':
        chord_tone[6] = True
        text += '-5'
    elif fifth == '#5':
        chord_tone[8] = True
        text += '+5'

    if third == 'Sus4':
        chord_tone[5] = True
        text += 'sus4'
    elif third == 'Sus2':
        chord_tone[2] = True
        text += 'sus2'

    if len(tensions) > 0:
        sorted_tensions = []
        if 'b9' in tensions:
            chord_tone[1] = True
            sorted_tensions.append('b9')
        if '9' in tensions:
            chord_tone[2] = True
            sorted_tensions.append('9')
        if '#9' in tensions:
            chord_tone[3] = True
            sorted_tensions.append('#9')
        if '11' in tensions:
            chord_tone[5] = True
            sorted_tensions.append('11')
        if '#11' in tensions:
            chord_tone[6] = True
            sorted_tensions.append('#11')
        if 'b13' in tensions:
            chord_tone[8] = True
            sorted_tensions.append('b13')
        if '13' in tensions:
            chord_tone[9] = True
            sorted_tensions.append('13')
        if third == 'Maj' or third == 'Min' or '3' in omits:
            if fifth == 'Perf' or '5' in omits:
                if sixth == None and seventh == None:
                    text += 'add' + sorted_tensions.pop(0)
        if len(sorted_tensions) > 0:
            text += f"({','.join(sorted_tensions)})"

    if len(omits) > 0:
        # text += f"(omit{','.join(omits)})"
        pass

    for flag1, flag2 in zip(chord_tone, original):
        if flag1 != flag2:
            raise Exception(f'ERROR: Failed to convert constituent notes to chords')

    return text

def chord_tone_from_text(text: str) -> List[bool]:
    pattern = r'(?P<power>5)?'
    pattern += r'(?(power)|(?P<third>m)?)'
    pattern += r'(?(power)|(?(third)|(?P<fifth>(dim|aug))?))'
    pattern += r'(?(power)|(?(fifth)|(?P<sixth>6)?))'
    pattern += r'(?(power)|(?(sixth)|(?P<seventh>M?7)?))'
    pattern += r'(?(power)|(?(sixth)|(?(seventh)|(?P<abbr_seventh>M?(9|11|13))?)))'
    pattern += r'(?(power)|(?P<acci_fifth>[#+b-]5)?)'
    pattern += r'(?(power)|(?(third)|(?(fifth)|(?P<sus>sus[24])?)))'
    add_tension_pattern = r'[#+b-]?9|[#+]?11|[b-]?13'
    pattern += rf'(?P<add>add({add_tension_pattern}))?'
    tension_pattern = rf'[#+b-]5|{add_tension_pattern}'
    pattern += rf'(?P<tensions>({tension_pattern})?(\(({tension_pattern})(?:,({tension_pattern}))*\))?)?'
    pattern += r'(?P<omits>(omit[35])?(\(omit[35](?:,([35]))*\))?)?'
    m = re.fullmatch(pattern ,text)

    if m is None:
        raise Exception('ERROR: Invalid string')

    power = m.group('power')
    third = m.group('third')
    fifth = m.group('fifth')
    sixth = m.group('sixth')
    seventh = m.group('seventh')
    abbr_seventh = m.group('abbr_seventh')
    acci_fifth = m.group('acci_fifth')
    sus = m.group('sus')
    add = m.group('add')
    tensions = m.group('tensions')
    omits = m.group('omits')

    if tensions is not None:
        tensions = re.findall(tension_pattern, tensions)
    else:
        tensions = []
    
    chord_tone = [False] * 12
    
    # Convert degree symbols to interval ('M3' -> 4)
    def degree_from_symbol(symbol: str) -> int:
        if symbol in ['R']:
            return 0
        if symbol in ['b9']:
            return 1
        if symbol in ['M2', '9']:
            return 2
        if symbol in ['m3', '#9']:
            return 3
        if symbol in ['M3']:
            return 4
        if symbol in ['P4', '11']:
            return 5
        if symbol in ['b5', '#11']:
            return 6
        if symbol in ['P5']:
            return 7
        if symbol in ['#5', 'b13']:
            return 8
        if symbol in ['M6', 'bb7', '13']:
            return 9
        if symbol in ['m7']:
            return 10
        if symbol in ['M7']:
            return 11
        
    # Add chord tone
    def add_note(symbol: str) -> None:
        idx = degree_from_symbol(symbol)
        if chord_tone[idx]:
            raise Exception(f'ERROR: Constituent already contains symbol at idx:{idx}')
        else:
            chord_tone[idx] = True
        
    # Remove chord tone
    def remove_note(symbol: str) -> None:
        idx = degree_from_symbol(symbol)
        chord_tone[idx] = False
            
    # Whether chord tone is contained
    def contains_note(symbol: str) -> bool:
        idx = degree_from_symbol(symbol)
        return chord_tone[idx]
    
    add_note('R')

    if power == '5':
        add_note('P5')
    elif sus is not None:
        if sus == 'sus2':
            add_note('M2')
        elif sus == 'sus4':
            add_note('P4')
    elif third == 'm' or fifth == 'dim':
        add_note('m3')
    else:
        add_note('M3')
    
    if fifth == 'dim':
        add_note('b5')
    elif fifth == 'aug':
        add_note('#5')
    elif power is None:
        add_note('P5')
        
    if sixth == '6':
        add_note('M6')

    if seventh == '7':
        if fifth == 'dim':
            add_note('bb7')
        else:
            add_note('m7')
    elif seventh == 'M7':
        add_note('M7')
        
    if abbr_seventh is not None:
        if abbr_seventh[0] == 'M':
            add_note('M7')
            abbr_seventh = abbr_seventh[1:]
        else:
            add_note('m7')
        if abbr_seventh == '9':
            tensions.append('9')
        elif abbr_seventh == '11':
            tensions.extend(['9', '11'])
        elif abbr_seventh == '13':
            tensions.extend(['9', '11', '13'])

    if acci_fifth is not None:
        if acci_fifth == 'b5' or acci_fifth == '-5':
            if contains_note('P5'):
                remove_note('P5')
                add_note('b5')
            else:
                add_note('#11')
        if acci_fifth == '#5' or acci_fifth == '+5':
            if contains_note('P5'):
                remove_note('P5')
                add_note('#5')
            else:
                add_note('b13')

    if add is not None:
        add = add[3:]
        if add == 'b9' or add == '-9':
            add_note('b9')
        if add == '9':
            add_note('9')
        if add == '#9' or add == '+9':
            add_note('#9')
        if add == '11':
            add_note('11')
        if add == '#11' or add == '+11':
            add_note('#11')
        if add == 'b13' or add == '-13':
            add_note('b13')
        if add == '13':
            add_note('13')

    if len(tensions) > 0:
        if 'b5' in tensions or '-5' in tensions:
            if contains_note('P5'):
                remove_note('P5')
                add_note('b5')
            else:
                add_note('#11')
        if '#5' in tensions or '+5' in tensions:
            if contains_note('P5'):
                remove_note('P5')
                add_note('#5')
            else:
                add_note('b13')
        if 'b9' in tensions or '-9' in tensions:
            add_note('b9')
        if '9' in tensions:
            add_note('9')
        if '#9' in tensions or '+9' in tensions:
            add_note('#9')
        if '11' in tensions:
            add_note('11')
        if '#11' in tensions or '+11' in tensions:
            add_note('#11')
        if 'b13' in tensions or '-13' in tensions:
            add_note('b13')
        if '13' in tensions:
            add_note('13')

    if '3' in omits:
        if contains_note('m3'):
            remove_note('m3')
        elif contains_note('M3'):
            remove_note('M3')
        else:
            raise Exception('ERROR: Third cannot be omitted because it is not included')
        
    if '5' in omits:
        if contains_note('b5'):
            remove_note('b5')
        elif contains_note('P5'):
            remove_note('P5')
        elif contains_note('#5'):
            remove_note('#5')
        else:
            raise Exception('ERROR: Fifth cannot be omitted because it is not included')
        
    return chord_tone