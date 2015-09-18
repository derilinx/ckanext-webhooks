import db
import logging

from ckan.lib.dictization import table_dictize
from ckan.logic import NotFound, check_access, ValidationError

import ckan.lib.navl.dictization_functions as df
import ckan.model as model

log = logging.getLogger(__name__)

schema = {
    'id': ['ignore_empty', unicode],
    'address': ['not_empty', unicode],
    'topic': ['not_empty', unicode],
    'user_id': ['ignore_missing', unicode],
    'created_at': ['ignore_missing', 'isodate']
}

schema_get = {
    'id': ['not_empty', unicode]
}

schema_list = {
    'topic': ['not_empty', unicode]
}

def webhook_create(context, data_dict):

    check_access("webhook_create", context, data_dict)

    data, errors = df.validate(data_dict, schema, context)

    if errors:
        raise ValidationError(errors)

    webhook = db.Webhook()
    webhook.address = data['address']
    webhook.topic = data['topic']
    webhook.user_id = model.User.get(context['user']).id
    webhook.save()

    session = context['session']
    session.add(webhook)
    session.commit()

    return webhook.id

def webhook_show(context, data_dict):
    check_access("webhook_show", context, data_dict)

    data, errors = df.validate(data_dict, schema_get, context)
    if errors:
        raise ValidationError(errors)

    webhook = db.Webhook.get(id=data['id'])
    if webhook is None:
        raise NotFound()

    return table_dictize(webhook, context)

def webhook_list(context, data_dict):
    check_access("webhook_list", context, data_dict)

    data, errors = df.validate(data_dict, schema_list, context)
    if errors:
        raise ValidationError(errors)

    webhooks = db.Webhook.find(topic=data['topic']).all()
    if webhooks is None:
        raise NotFound()

    ids = [webhook.id for webhook in webhooks]

    return ids

def webhook_delete(context, data_dict):
    check_access("webhook_delete", context, data_dict)

    data, errors = df.validate(data_dict, schema_get, context)
    if errors:
        raise ValidationError(errors)

    webhook = db.Webhook.get(id=data['id'])
    if webhook is None:
        raise NotFound()

    session = context['session']
    session.delete(webhook)
    session.commit()

    return data['id']
