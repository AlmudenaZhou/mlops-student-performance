if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    columns_to_consider = ['ParentalEducation', 'StudyTimeWeekly', 'Absences', 
                           'Tutoring', 'ParentalSupport', 'Extracurricular', 
                           'Sports', 'Music', 'Volunteering', 'GradeClass']

    return data.loc[:, columns_to_consider]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
