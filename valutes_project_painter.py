from valutes_project_settings import params_default
from valutes_project_lib import get_data_from_db, draw_plot, get_analys_text


def valutes_painter(valutes, period, show_min_max_plot, night_theme) -> tuple:
    # получаем DataFrame
    df = get_data_from_db(button_first=valutes, button_second=period)
    # проверка на пустой датафрейм
    if df.empty:
        return None, 'DataFrame is Empty!'

    else:
        # получаем картинку
        picture: bytes = draw_plot(df=df, x_count=params_default['x_count'], y_count=params_default['y_count'], \
                            font_size=params_default['font_size'], \
                            show_min_max_plot=show_min_max_plot, \
                            night_theme_on=night_theme, \
                            button_first=valutes, \
                            button_second=period)
        # получаем подпись к картинке
        caption: str = get_analys_text(df, valutes, period)
        return picture, caption
