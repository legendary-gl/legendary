from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from epic_expreval import Tokenizer
from legendary.utils.selective_dl import LGDEvaluationContext, EXTRA_FUNCTIONS

def get_boolean_choice(prompt, default=True):
    yn = 'Y/n' if default else 'y/N'

    choice = input(f'{prompt} [{yn}]: ')
    if not choice:
        return default
    elif choice[0].lower() == 'y':
        return True
    else:
        return False


def get_int_choice(prompt, default=None, min_choice=None, max_choice=None, return_on_invalid=False):
    if default is not None:
        prompt = f'{prompt} [{default}]: '
    else:
        prompt = f'{prompt}: '

    while True:
        try:
            if inp := input(prompt):
                choice = int(inp)
            else:
                return default
        except ValueError:
            if return_on_invalid:
                return None
            return_on_invalid = True
            continue
        else:
            if min_choice is not None and choice < min_choice:
                print(f'Number must be greater than {min_choice}')
                if return_on_invalid:
                    return None
                return_on_invalid = True
                continue
            if max_choice is not None and choice > max_choice:
                print(f'Number must be less than {max_choice}')
                if return_on_invalid:
                    return None
                return_on_invalid = True
                continue
            return choice


def sdl_prompt(sdl_data, title, context):
    print(f'You are about to install {title}, this application supports selective downloads.')
    choices = []
    required_categories = {}
    for element in sdl_data['Data']:
        is_required = element.get('IsRequired', 'false').lower() == 'true'
        has_children = 'Children' in element
        is_invisible = element.get('Invisible', 'false').lower() == 'true'
        if (is_required and not has_children) or is_invisible:
            continue
        
        if element.get('ConfigHandler'):
            choices.append(Separator(4 * '-' + ' ' + element['Title'] + ' ' + 4 * '-'))
            is_required = element.get('IsRequired', 'false').lower() == 'true'
            if is_required: required_categories[element['UniqueId']] = []
            for child in element.get('Children', []):
                enabled = element.get('IsDefaultSelected', 'false').lower() == 'true'
                choices.append(Choice(child['UniqueId'], name=child['Title'], enabled=enabled))
                if is_required: required_categories[element['UniqueId']].append(child['UniqueId'])
        else:
            enabled = False
            if element.get('IsDefaultSelected', 'false').lower() == 'true':
                expression = element.get('DefaultSelectedExpression')
                if expression:
                    tk = Tokenizer(expression, context)
                    tk.extend_functions(EXTRA_FUNCTIONS)
                    tk.compile()
                    if tk.execute(''):
                        enabled = True
                else:
                    enabled = True
            choices.append(Choice(element['UniqueId'], name=element['Title'], enabled=enabled))

    selected_packs = inquirer.checkbox(message='Select optional packs to install',
                                       choices=choices,
                                       cycle=True,
                                       validate=lambda selected: not required_categories or all(any(item in selected for item in category) for category in required_categories.values())).execute()
    return selected_packs


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    Copied from python standard library as distutils.util.strtobool is deprecated.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0', ''):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))

