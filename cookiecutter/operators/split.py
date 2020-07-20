# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class SplitOperator(BaseOperator):
    """
    Operator for PyInquirer type prompts.

    :param items: A list of string to split or just a string
    :param separator: String separator
    :return: List if input items is list otherwise string
    """

    type = 'split'

    def __init__(self, *args, **kwargs):  # noqa
        super(SplitOperator, self).__init__(*args, **kwargs)

        self.separator = (
            self.operator_dict['separator']
            if 'separator' in self.operator_dict
            else "."
        )

    def _execute(self):
        if isinstance(self.operator_dict['items'], str):
            # If item is a string then return a list
            return self.operator_dict['items'].split(self.separator)
        elif isinstance(self.operator_dict['items'], list):
            # If items is a list then return a nested list
            output = []
            for i in self.operator_dict['items']:
                output.append(i.split('-'))
            return output
        else:
            raise NotImplementedError(
                "Have not implemented dict input to " "`items` for `type` 'split'"
            )
