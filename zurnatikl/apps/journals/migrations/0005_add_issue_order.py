# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def guess_issue_sort_order(apps, schema_editor):
    Journal = apps.get_model("journals", "Journal")
    for j in Journal.objects.all():
        sort_order = 0
        for i in j.issue_set.all().order_by('publication_date'):
            i.sort_order = sort_order
            i.save()
            sort_order += 1

# NOTE: in django 1.8 use RunPython.noop
def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0004_journal_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='sort_order',
            field=models.PositiveSmallIntegerField(help_text=b'Sort order for display within a journal', null=True, verbose_name=b'Sort order', blank=True),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['journal', 'order', 'volume', 'issue']},
        ),
        migrations.RunPython(guess_issue_sort_order, noop),
    ]
