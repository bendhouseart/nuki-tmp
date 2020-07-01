# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class InquirerCheckboxOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'checkbox'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize PyInquirer 'checkbox` type prompt."""  # noqa
        super(InquirerCheckboxOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Run the prompt."""  # noqa
        if not self.no_input:
            if 'name' not in self.operator_dict:
                self.operator_dict.update({'name': 'tmp'})
                return prompt([self.operator_dict])['tmp']
            else:
                return prompt([self.operator_dict])
        elif 'default' in self.operator_dict:
            return self.operator_dict['default']
        else:
            # When no_input then return empty list
            return []
