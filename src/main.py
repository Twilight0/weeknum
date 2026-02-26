import flet as ft
import datetime
import asyncio

from utils import get_week_and_year, get_date_range, get_todays_wiki

async def main(page: ft.Page):

    page.title = "Weeknum"
    page.scroll = ft.ScrollMode.AUTO

    locale_format = await ft.SharedPreferences().contains_key("format")
    if locale_format:
        locale_format = await ft.SharedPreferences().get("format")
    else:
        locale_format = 'local'

    def apply_formats():

        abbreviated_format = '%b %d'

        if locale_format == 'us':
            regular_date_format = '%m/%d/%Y'
        elif locale_format == 'eu':
            regular_date_format = '%d.%m.%Y'
            abbreviated_format = '%d %b'
        elif locale_format == 'iso8601':
            regular_date_format = '%Y-%m-%d'
        else:
            regular_date_format = '%x'

        return regular_date_format, abbreviated_format

    stored_theme = await ft.SharedPreferences().contains_key("theme_mode")
    if stored_theme:
        stored_theme = await ft.SharedPreferences().get("theme_mode")
    page.theme_mode = (
        ft.ThemeMode.DARK if stored_theme == "dark" else ft.ThemeMode.LIGHT
    )

    today = datetime.date.today()

    current_week, current_year = get_week_and_year(today)
    week_start = await ft.SharedPreferences().contains_key("week_start")
    if week_start:
        week_start = await ft.SharedPreferences().get("week_start")
    else:
        week_start = 'monday'
    start_date, end_date = get_date_range(current_year, current_week, week_start)

    week_display = ft.Text(
        f"Week: {current_week}", size=20, weight=ft.FontWeight.BOLD
    )
    year_display = ft.Text(f"{current_year}", size=25, italic=True)
    date_display = ft.Text(
        f"{start_date.strftime(apply_formats()[1])} - {end_date.strftime(apply_formats()[1])}",
        size=24
    )

    total_days = (datetime.date(current_year + 1, 1, 1) - datetime.date(current_year, 1, 1)).days
    remaining_days = total_days - int(today.strftime("%j"))
    date_text = f"Current date: {today.strftime(apply_formats()[0])}, day: {today.strftime("%j")}/{total_days}, remaining: {remaining_days}"
    current_date_display = ft.Text(date_text, size=12, italic=True)

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    async def close_dialog_and_drawer(dialog, close_drawer=False):
        dialog.open = False
        if close_drawer:
            await page.close_drawer()
        page.update()

    def update_formats(rdf, af):
        nonlocal current_date_display, date_display
        current_date_display.value = f"Current date: {today.strftime(rdf)}, day: {today.strftime("%j")}/{total_days}, remaining: {remaining_days}"
        date_display.value = f"{start_date.strftime(af)} - {end_date.strftime(af)}"

    def update_week(year, week):
        nonlocal current_week, current_year, start_date, end_date
        current_week, current_year = week, year
        start_date, end_date = get_date_range(current_year, current_week, week_start)
        week_display.value = f"Week: {current_week}"
        year_display.value = f"{current_year}"
        date_display.value = (
            f"{start_date.strftime(apply_formats()[1])} - "
            f"{end_date.strftime(apply_formats()[1])}"
        )

    def on_prev_click(e):
        d = datetime.date.fromisocalendar(current_year, current_week, 1) - datetime.timedelta(days=7)
        w, y = get_week_and_year(d)
        update_week(y, w)
        page.update()

    def on_next_click(e):
        d = datetime.date.fromisocalendar(current_year, current_week, 1) + datetime.timedelta(days=7)
        w, y = get_week_and_year(d)
        update_week(y, w)
        page.update()

    def enter_week_dialog(e):

        week_field = ft.TextField(label="Week", value=str(current_week))
        year_field = ft.TextField(label="Year", value=str(current_year))

        def on_submit(ev):
            week_field.error = None
            year_field.error = None
            try:
                w = int(week_field.value)
                y = int(year_field.value)
                get_date_range(y, w, week_start)
                update_week(y, w)
                close_dialog(dialog)
            except ValueError:
                week_field.error = "Invalid input"
                year_field.error = "Invalid input"
            finally:
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enter Week and Year"),
            content=ft.Column([week_field, year_field]),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog)),
                ft.Button("OK", on_click=on_submit),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def enter_date_dialog(e):

        date_field = ft.TextField(label=f"Format: YYYY-MM-DD")

        def on_submit(ev):
            try:
                date = datetime.datetime.strptime(date_field.value, "%Y-%m-%d").date()
                w, y = get_week_and_year(date)
                update_week(y, w)
                dialog.open = False
            except ValueError:
                date_field.error = "Invalid input format"
            finally:
                page.update()

        def on_today():
            update_week(*reversed(get_week_and_year(datetime.date.today())))
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enter a valid date"),
            content=ft.Column([date_field]),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog)),
                ft.Button("Today", on_click=on_today),
                ft.Button("OK", on_click=on_submit),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def show_the_day():

        date_field = ft.TextField(label=f"Format: YYYY-MM-DD")

        async def on_submit():

            try:
                date_obj = datetime.datetime.strptime(date_field.value, "%Y-%m-%d").date()
                dlg = ft.AlertDialog(
                    title=ft.Text(date_obj.strftime("%A")),
                    actions=[ft.Button("Dismiss", on_click=lambda _: page.pop_dialog())]
                )
                await close_dialog_and_drawer(dialog)
                page.show_dialog(dlg)
            except ValueError:
                date_field.error = "Invalid format"
            finally:
                page.update()

        async def on_today():

            dlg = ft.AlertDialog(
                title=ft.Text(today.strftime("%A")),
                actions=[ft.Button("Dismiss", on_click=lambda _: page.pop_dialog())]
            )
            dialog.open = False
            page.show_dialog(dlg)
            page.update()
            await close_dialog_and_drawer(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Enter a valid date"),
            content=ft.Column([date_field]),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog)),
                ft.Button("Today", on_click=on_today),
                ft.Button("OK", on_click=on_submit),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def change_format():

        async def select_format(f):

            nonlocal locale_format
            locale_format = f

            await ft.SharedPreferences().set("format", f)
            await close_dialog_and_drawer(dialog, close_drawer=True)
            update_formats(*apply_formats())
            page.update()

        # Async wrappers for buttons
        async def iso8601_handler(e):
            await select_format("iso8601")
        async def us_handler(e):
            await select_format("us")
        async def eu_handler(e):
            await select_format("eu")
        async def local_handler(e):
            await select_format("local")

        dialog = ft.AlertDialog(
            title=ft.Text("Select format"),
            content=ft.Column(
                [
                    ft.Button("ISO 8601: YYYY-MM-DD", on_click=iso8601_handler),
                    ft.Button("US Date: MM/DD/YYYY", on_click=us_handler),
                    ft.Button("EU Date: DD.MM.YYYY", on_click=eu_handler),
                    ft.Button("Local", on_click=local_handler)
                ]
            ),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog)),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def change_week_start():
        nonlocal week_start

        async def select_day(day):
            nonlocal week_start
            await ft.SharedPreferences().set("week_start", day)
            week_start = day
            update_week(current_year, current_week)
            close_dialog(dialog)

            async def close_drawer_and_snack():
                await page.close_drawer()

                page.show_dialog(
                    ft.SnackBar(
                        content=ft.Text(f"Day selected: {week_start.capitalize()}"),
                        behavior=ft.SnackBarBehavior.FLOATING,
                        duration=2000
                    )
                )
                page.update()

            page.run_task(close_drawer_and_snack)
            page.update()

        async def monday_handler(e): await select_day("monday")

        async def sunday_handler(e): await select_day("sunday")

        async def saturday_handler(e): await select_day("saturday")

        # Create AlertDialog
        dialog = ft.AlertDialog(
            title=ft.Text("Choose week start day"),
            content=ft.Column([
                ft.Text(f"Currently: {week_start.title()}"),
                ft.Button("Monday", on_click=monday_handler),
                ft.Button("Sunday", on_click=sunday_handler),
                ft.Button("Saturday", on_click=saturday_handler),
            ]),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog)),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    async def toggle_theme():
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            await ft.SharedPreferences().set("theme_mode", "dark")
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            await ft.SharedPreferences().set("theme_mode", "light")
        page.update()

    async def open_github(e):
        await ft.UrlLauncher().launch_url("https://github.com/Twilight0/weeknum/")
        await page.close_drawer()

    async def handle_link_tap(e: ft.Event[ft.Markdown]):
        await page.launch_url(e.data)

    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.ListTile(title=ft.Text("Toggle Theme"), on_click=toggle_theme),
            ft.ListTile(title=ft.Text("Change week start day"), on_click=change_week_start),
            ft.ListTile(title=ft.Text("Formats"), on_click=change_format),
            ft.ListTile(title=ft.Text("What day is it?"), on_click=show_the_day),
            ft.ListTile(title=ft.Text("About"), on_click=open_github),
        ]
    )

    main_row = ft.Row(
        [
            ft.Button(content=ft.Icon(ft.Icons.ARROW_LEFT, size=50), on_click=on_prev_click),
            ft.Button(
                content=ft.Column(
                    [week_display, year_display],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    on_click=enter_week_dialog
            ),
            ft.Button(content=ft.Icon(ft.Icons.ARROW_RIGHT, size=50), on_click=on_next_click),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    middle_display = ft.Button(
        content=date_display, expand=True, on_click=enter_date_dialog, height=60
    )

    bottom_display = ft.Button(
        icon=ft.Icons.CALENDAR_MONTH,
        content=ft.Text(
            'What day is it?', size=24, italic=True
        ),
        expand=True,
        on_click=show_the_day,
        height=60
    )

    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, on_click=page.show_drawer),
        title=current_date_display,
        center_title=True
    )

    # Create a placeholder for the wiki content
    wiki_display = ft.Column(
        [
            ft.ProgressBar(),
            ft.Text("Fetching today's history...", italic=True)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(ft.Column([main_row, middle_display, bottom_display, wiki_display], horizontal_alignment=ft.CrossAxisAlignment.STRETCH))
    page.update()

    # Fetch the wiki data
    wiki = await asyncio.to_thread(get_todays_wiki)

    # Process the wiki text for better formatting using Markdown
    lines = wiki.strip().split('\n')
    markdown_text = ""
    for count, line in list(enumerate(lines, start=1)):
        if count == 1:
            markdown_text += f"# {line}\n"
        elif count == 2:
            markdown_text += line.replace(line, '---\n')
        elif ' – ' in line:
            # Split at the first occurrence of the en-dash
            parts = line.split(' – ', 1)
            year = parts[0]
            description = parts[1]
            # Format as a bullet point with the year bolded
            markdown_text += f"* **{year}** – {description}\n"

    markdown_text += '[Read more...](https://en.wikipedia.org/wiki/Wikipedia:On_this_day/Today)'

    wiki_display.controls = [ft.Container(content=ft.Markdown(
        markdown_text,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.COMMON_MARK,
        on_tap_link=handle_link_tap,
    ), padding=10)]
    page.update()
    #
    # page.window.width = 720
    # page.window.height = 1280
    # page.update()
    # await page.window.center()

ft.run(main)
