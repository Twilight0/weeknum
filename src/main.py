import flet as ft
import datetime
import locale

from utils import get_week_and_year, get_date_range

def close_dialog(dialog, page):
    dialog.open = False
    page.update()


async def main(page: ft.Page):
    page.title = "Weeknum"

    # --- Theme loading ---
    stored_theme = await ft.SharedPreferences().get("theme_mode")
    page.theme_mode = (
        ft.ThemeMode.DARK if stored_theme == "dark" else ft.ThemeMode.LIGHT
    )

    page.window_resizable = False
    page.window_width = 300
    page.window_height = 400

    today = datetime.date.today()

    try:
        locale.setlocale(locale.LC_TIME, "")
    except locale.Error:
        text = "Failed to set locale"
        print(text)
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(f"{text}"),
                behavior=ft.SnackBarBehavior.FLOATING
            )
        )
        page.update()

    current_week, current_year = get_week_and_year(today)
    week_start = await ft.SharedPreferences().get("week_start") or "monday"
    start_date, end_date = get_date_range(current_year, current_week, week_start)

    week_display = ft.Text(
        f"Week: {current_week}", size=20, weight=ft.FontWeight.BOLD
    )
    year_display = ft.Text(f"{current_year}", size=25, italic=True)
    date_display = ft.Text(
        f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}", size=24
    )

    today_ = today.strftime("%x")

    current_date_text = ft.Text(f"Current date: {today_}", size=12, italic=True)

    def update_week(year, week):
        nonlocal current_week, current_year, start_date, end_date
        current_week, current_year = week, year
        start_date, end_date = get_date_range(current_year, current_week, week_start)
        week_display.value = f"Week: {current_week}"
        year_display.value = f"{current_year}"
        date_display.value = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"


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

    # --- Week dialog ---
    def enter_week_dialog(e):

        week_field = ft.TextField(label="Week", value=str(current_week))
        year_field = ft.TextField(label="Year", value=str(current_year))

        def on_submit(ev):
            week_field.error_text = None
            year_field.error_text = None
            try:
                w = int(week_field.value)
                y = int(year_field.value)
                get_date_range(y, w, week_start)
                update_week(y, w)
                close_dialog(dialog, page)
                page.update()
            except ValueError:
                week_field.error_text = "Invalid week/year"
                year_field.error_text = "Invalid week/year"
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enter Week and Year"),
            content=ft.Column([week_field, year_field]),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog, page)),
                ft.Button("OK", on_click=on_submit),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- Date dialog ---
    def enter_date_dialog(e):

        date_field = ft.TextField(label="Format: YYYY-MM-DD")

        def on_submit(ev):
            try:
                date = datetime.datetime.strptime(date_field.value, "%Y-%m-%d").date()
                w, y = get_week_and_year(date)
                update_week(y, w)
                dialog.open = False
                page.update()
            except ValueError:
                date_field.error_text = "Invalid date"
                page.update()

        def on_today():
            update_week(*reversed(get_week_and_year(datetime.date.today())))
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enter a valid date"),
            content=ft.Column([date_field]),
            actions=[
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog, page)),
                ft.Button("Today", on_click=on_today),
                ft.Button("OK", on_click=on_submit),
            ],
            modal=True,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- Async actions ---
    async def change_week_start():
        nonlocal week_start

        async def select_day(day):
            nonlocal week_start
            # Save selection
            await ft.SharedPreferences().set("week_start", day)
            week_start = day
            update_week(current_year, current_week)

            # Close dialog
            close_dialog(dialog, page)

            # Close drawer and show snackbar after
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

            # Schedule properly
            page.run_task(close_drawer_and_snack)

        # Async wrappers for buttons
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
                ft.Button("Cancel", on_click=lambda _: close_dialog(dialog, page)),
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

    async def toggle_theme_handler(e):
        await toggle_theme()

    async def change_week_start_handler(e):
        await change_week_start()

    async def open_github(e):
        await ft.UrlLauncher().launch_url("https://github.com/Twilight0/Weeknum")
        await page.close_drawer()

    async def show_drawer(e):
        await page.show_drawer()

    # --- Drawer ---
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.ListTile(title=ft.Text("Toggle Theme"), on_click=toggle_theme_handler),
            ft.ListTile(title=ft.Text("Change Week Start Day"), on_click=change_week_start_handler),
            ft.ListTile(title=ft.Text("GitHub Repo"), on_click=open_github),
        ]
    )

    # --- Main UI ---
    main_row = ft.Row(
        [
            ft.Button(content=ft.Icon(ft.Icons.ARROW_LEFT, size=50), on_click=on_prev_click),
            ft.Button(
                content=ft.Column([week_display, year_display],
                                  alignment=ft.MainAxisAlignment.CENTER,
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                on_click=enter_week_dialog,
            ),
            ft.Button(content=ft.Icon(ft.Icons.ARROW_RIGHT, size=50), on_click=on_next_click),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    bottom_display = ft.Button(content=date_display, expand=True, on_click=enter_date_dialog, height=60)

    page.appbar = ft.AppBar(leading=ft.IconButton(ft.Icons.MENU, on_click=show_drawer), title=current_date_text)

    page.add(ft.Column([main_row, bottom_display], horizontal_alignment=ft.CrossAxisAlignment.STRETCH))

ft.run(main)
