import datetime
import calendar


def get_day_name(weekday):
    """
    This function gets the number of the day considering
    the week and returns a String. The string corresponds
    to the name of the weekday in Portuguese.

    :param weekday:         int
                            The weekday is generated by a
                            function of datetime package:

    :return:                String

    Example of weekday:

    import datetime
    weekday = datetime.datetime.strptime(date, '%d %m %Y').weekday()
    """

    if weekday == 0:
        return "Seg"
    elif weekday == 1:
        return "Ter"
    elif weekday == 2:
        return "Qua"
    elif weekday == 3:
        return "Qui"
    elif weekday == 4:
        return "Sex"
    elif weekday == 5:
        return "Sáb"
    else:
        return "Dom"


def date_time_pt(date):
    """
    This function gets the name of the weekday according to
    a date. It returns a string that corresponds to the name
    of the weekday in Portuguese.

    :param date:        String
                        'Day Month Year'
                        Ex: '25 01 2021'

    :return:            int
                        The number of the week
                        Monday: 0
                        Tuesday: 1
                        ...
    """
    number_day = datetime.datetime.strptime(date, '%d %m %Y').weekday()
    weekday_pt = get_day_name(number_day)
    return weekday_pt


def date_time_en(date):
    """
    This function gets the name of the weekday according to
    a date. It returns a string that corresponds to the name
    of the weekday in English.

    :param date:        String
                        'Day Month Year'
                        Ex: '25 01 2021'

    :return:            int
                        The number of the week
                        Monday: 0
                        Tuesday: 1
                        ...
    """
    number_day = datetime.datetime.strptime(date, '%d %m %Y').weekday()
    weekday_en = calendar.day_name[number_day]
    return weekday_en


