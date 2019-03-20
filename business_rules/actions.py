from __future__ import absolute_import
import inspect

from .utils import fn_name_to_pretty_label, get_valid_fields


class BaseActions(object):
    """ Classes that hold a collection of actions to use with the rules
    engine should inherit from this.
    """

    @classmethod
    def get_all_actions(cls):
        methods = inspect.getmembers(cls)
        return [{
                    'name': m[0],
                    'label': m[1].label,
                    'params': m[1].params
                } for m in methods if getattr(m[1], 'is_rule_action', False)]


def _validate_action_parameters(func, params):
    """
    Verifies that the parameters specified are actual parameters for the
    function `func`, and that the field types are FIELD_* types in fields.
    :param func:
    :param params:
    :return:
    """
    if params is not None:
        # Verify field name is valid
        valid_fields = get_valid_fields()

        for param in params:
            param_name, field_type = param['name'], param['fieldType']
            default_value = param.get('defaultValue')
            if param_name not in func.__code__.co_varnames and not default_value:
                raise AssertionError("Unknown parameter name {0} specified for action {1}".format(
                    param_name, func.__name__))

            if field_type not in valid_fields:
                raise AssertionError("Unknown field type {0} specified for action {1} param {2}".format(
                    field_type, func.__name__, param_name))


def rule_action(label=None, params=None):
    """
    Decorator to make a function into a rule action.

    NOTE: add **kwargs argument to receive Rule and Matched Conditions as parameters in Action function

    :param label: Label for Action
    :param params: Parameters expected by the Action function
    :return: Decorator function wrapper
    """

    def wrapper(func):
        params_ = params
        if isinstance(params, dict):
            params_ = [
                dict(
                    label=fn_name_to_pretty_label(key),
                    name=key,
                    fieldType=getattr(value, "field_type", value),
                    defaultValue=getattr(value, "default_value", None)
                ) for key, value in params.items()
            ]

        _validate_action_parameters(func, params_)

        func.is_rule_action = True
        func.label = label or fn_name_to_pretty_label(func.__name__)
        func.params = params_

        return func

    return wrapper


class ActionParam:
    def __init__(self, field_type, default_value=None):
        self.field_type = field_type
        self.default_value = default_value
