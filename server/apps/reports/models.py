from django.db.models import Count, Sum

from apps.survey.models import Question, LocationAnswer, MultiAnswer


class QuestionReport(Question):

    class Meta:
        proxy = True

    def get_answer_domain(self, survey, filters=None):
        answers = self.response_set.all()  # self.response_set.filter(respondant__complete=True)
        if self.type in ['map-multipoint']:
            locations = LocationAnswer.objects.filter(location__response__in=answers)
        if filters is not None:
            for filter in filters:
                slug = filter.keys()[0]
                value = filter[slug]
                filter_question = QuestionReport.objects.get(slug=slug, survey=survey)

                if self.type in ['map-multipoint']:
                    if filter_question == self:
                        locations = locations.filter(answer__in=value)
                    else:
                        answers = answers.filter(respondant__responses__in=filter_question.response_set.filter(answer__in=value))
                        locations = locations.filter(location__response__in=answers)
                else:
                    answers = answers.filter(respondant__responses__in=filter_question.response_set.filter(answer__in=value))
        if self.type in ['map-multipoint']:
            return locations.values('answer').annotate(locations=Count('answer'), surveys=Count('location__respondant', distinct=True))
        elif self.type in ['multi-select']:
            return (MultiAnswer.objects.filter(response__in=answers)
                                       .values('answer_text')
                                       .annotate(surveys=Count('answer_text')))
        else:
            return (answers.values('answer')
                           .annotate(locations=Sum('respondant__locations'), surveys=Count('answer')))
