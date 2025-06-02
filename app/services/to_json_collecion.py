from flask import current_app, url_for


def to_json_collection(resources, endpoint, **kwargs):
    data = {
        'items': [item.to_dict() for item in resources.items],
        '_meta': {
            'page': resources.page,
            'per_page': resources.per_page,
            'total_pages': resources.pages,
            'total_items': resources.total
        },
        '_links': {
            'self': url_for(endpoint, page=resources.page, **kwargs),
            'next': url_for(endpoint, page=resources.page + 1,
                            **kwargs) if resources.has_next else None,
            'prev': url_for(endpoint, page=resources.page - 1,
                            **kwargs) if resources.has_prev else None
        }
    }
    current_app.logger.info(f'data: {data}')
    return data
