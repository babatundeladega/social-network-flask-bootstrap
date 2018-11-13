from flask import current_app, request
from flask_sqlalchemy import BaseQuery

from app.constants import statuses
from app.errors import BadRequest


class CustomQuery(BaseQuery):

    def paginate(self,
                 page=None,
                 per_page=None,
                 error_out=False,
                 max_per_page=None,
                 use_request_args=True):
        app = current_app

        if use_request_args:
            # TODO:
            # This assumes pagination parameters are specified
            # as URL query parameters and not in body payload.
            params = request.args

            try:
                page = int(params.get('page', 0))
                per_page = int(params.get('per_page', 0))
            except (TypeError, ValueError):
                raise BadRequest('Pagination parameters should be integers.')

            page = page or app.config['PAGINATION_DEFAULT_PAGE']
            per_page = per_page or app.config['PAGINATION_DEFAULT_PER_PAGE']

        max_per_page = max_per_page or app.config['PAGINATION_DEFAULT_PER_PAGE']

        pagination = super(CustomQuery,
                           self).paginate(page=int(page),
                                          per_page=int(per_page),
                                          error_out=error_out,
                                          max_per_page=int(max_per_page))

        pagination.meta = {
            'pagination': {
                'previous_page': (pagination.prev_num if
                                  pagination.has_prev else None),
                'next_page': (pagination.next_num if
                              pagination.has_next else None),
                'num_items': pagination.total,
                'num_pages': pagination.pages,
                'has_next_page': pagination.has_next,
                'has_previous_page': pagination.has_prev
            }
        }

        return pagination
