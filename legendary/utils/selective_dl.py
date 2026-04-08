# This file contains utilities for selective downloads in regards to parsing and evaluating sdlmeta
# coding: utf-8

import os
import json
from epic_expreval import Tokenizer, EvaluationContext

def has_access(context, app):
    return bool(context.core.get_game(app))

def is_selected(context, input):
    return input in context.selection

false_lambda = lambda c,i: False

EXTRA_FUNCTIONS = {
    'HasAccess': has_access,
    "IsComponentSelected": is_selected,
    "D3D12FeatureDataOptions1Check": false_lambda,
    "D3D12FeatureDataOptions2Check": false_lambda,
    "D3D12FeatureDataOptions3Check": false_lambda,
    "D3D12FeatureDataOptions4Check": false_lambda,
    "D3D12FeatureDataOptions5Check": false_lambda,
    "D3D12FeatureDataOptions6Check": false_lambda,
    "D3D12FeatureDataOptions7Check": false_lambda,
    "D3D12FeatureDataOptions9Check": false_lambda,
    "D3D12FeatureDataOptions9Check": false_lambda,
    "IsIntelAtomic64EmulationSupported": false_lambda
}

class LGDEvaluationContext(EvaluationContext):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.selection = set()

    def reset(self):
        super().reset()
        self.selection = set()

def run_expression(expression, input):
    """Runs expression with default EvauluationContext"""
    tk = Tokenizer(expression, EvaluationContext())
    tk.compile()
    return tk.execute(input)

def get_sdl_data(location, app_name, app_version):
    applying_meta = []
    for sdmeta_file in location.glob('*sdmeta'):
        sdmeta = json.loads(sdmeta_file.read_text('utf-8-sig'))
        is_applying_build = any(
            build
            for build in sdmeta.get('Builds')
            if build.get('Asset') == app_name
            and run_expression(build['Version'], app_version)
        )
        if is_applying_build:
            applying_meta.append(sdmeta)
            
    if applying_meta:
        return applying_meta[-1]
    return None

def parse_components_selection(sdl_data, eval_context, install_components, install_tags):
    for element in sdl_data['Data']:
        if element.get('IsRequired', 'false').lower() == 'true':
            install_tags.update(element.get('Tags', []))
            if element['UniqueId'] not in install_components:
                install_components.append(element['UniqueId'])
            continue
        if element.get('Invisible', 'false').lower() == 'true':
            tk = Tokenizer(element['InvisibleSelectedExpression'], eval_context)
            tk.extend_functions(EXTRA_FUNCTIONS)
            tk.compile()
            if tk.execute(''):
                install_tags.update(element.get('Tags', []))
                if element['UniqueId'] not in install_components:
                    install_components.append(element['UniqueId'])

        # The ids may change from revision to revision, this property lets us match options against older options
        upgrade_id = element.get('UpgradePathLogic')
        if upgrade_id and upgrade_id in install_components:
            install_tags.update(element.get('Tags', []))
            # Replace component id with upgraded one
            install_components = [element['UniqueId'] if el == upgrade_id else el for el in install_components]

        if element['UniqueId'] in install_components:
            install_tags.update(element.get('Tags', []))

        if element.get('ConfigHandler'):
            for child in element.get('Children', []):
                if child['UniqueId'] in install_components:
                    install_tags.update(child.get('Tags', []))
