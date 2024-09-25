import os
from datetime import datetime

import pandas as pd
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from matplotlib import pyplot as plt
from meteostat import Point, Daily

from Maplayout import MapLayout
from CountryCityInput import CountryCityInput

class ContentPopup(Popup):
    pass


class WeatherApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        root = Builder.load_file(os.path.join(os.getcwd(), "kvfile\\App.kv"))
        return root

    def go_press(self):
        print(self.root.ids)

    def show_date_picker(self, date_type):
        date_dialog = MDDatePicker(year=datetime.now().year)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
        self.date_type = date_type

    def on_save(self, instance, value, date_range):
        if self.date_type == 'start':
            self.root.ids.calendar.ids.start_date_label.text = str(value)
        else:
            self.root.ids.calendar.ids.end_date_label.text = str(value)

    def on_cancel(self, instance, value):
        pass

    def get_weather(self):
        print(self.root.ids.map_window.ids.mapview.lat, self.root.ids.map_window.ids.mapview.lon)
        print(self.root.ids)
        self.root.ids.country_city_input.on_go_button_pressed()
        latitude = self.root.ids.map_window.ids.mapview.lat
        longitude = self.root.ids.map_window.ids.mapview.lon
        print(self.root.ids)
        start_datetime = None
        end_datetime = None
        if self.root.ids.calendar.ids.start_date_label.text == "":
            print("no date selected")
        else:
            start_datetime = self.string_to_date_obj(self.root.ids.calendar.ids.start_date_label.text)
        if self.root.ids.calendar.ids.end_date_label.text == "":
            print("no date selected")
        else:
            end_datetime = self.string_to_date_obj(self.root.ids.calendar.ids.start_date_label.text)
        if start_datetime and end_datetime:
            location = Point(latitude, longitude)
            data = Daily(location, start=start_datetime, end=end_datetime).fetch()
            print(data.to_string())
            data.to_csv("data.csv")
            self.plot_weather_data()
        pass

    def string_to_date_obj(self, string):
        datetime_string = string
        print(datetime_string)
        datetime_format = "%Y-%m-%d"
        date_object = datetime.strptime(datetime_string, datetime_format)
        datetime_object = datetime.combine(date_object, datetime.min.time())
        print(datetime_object)
        return datetime_object

    def plot_weather_data(self):
        df = pd.read_csv('data.csv', parse_dates=['time'], index_col='time')

        summary_message = ""
        for col in df.columns:
            summary_message += f'{col}:\n'
            summary_message += f'  Min: {df[col].min()}\n'
            summary_message += f'  Max: {df[col].max()}\n'
            summary_message += f'  Average: {round(df[col].mean(), 1)}\n'
            summary_message += '\n'

        fig, axes = plt.subplots(nrows=len(df.columns), ncols=1, figsize=(12, 20), sharex=True)
        for i, col in enumerate(df.columns):
            axes[i].plot(df.index, df[col], label=col)
            axes[i].set_ylabel(col)
            axes[i].legend(loc='best')
            axes[i].grid(True)
        axes[-1].set_xlabel('Date')
        fig.suptitle('Weather Data Over Time', fontsize=16)
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)
        plot_widget = FigureCanvasKivyAgg(fig)
        self.show_popup("Weather Data", summary_message, plot_widget)

    def show_popup(self, title, message, plot_widget=None):
        popup = ContentPopup()
        popup.title = title
        print(f"popping {message}")

        dictionaryy = message.split('\n\n')
        newdict = [dictionaryy[i] + "\n" + dictionaryy[i + 1] if i + 1 < len(dictionaryy) else dictionaryy[i] for i in
                   range(0, len(dictionaryy), 2)]
        for i in range(0, len(newdict)):
            popup.ids.weather_label.add_widget(Label(text=newdict[i]))
        if plot_widget:
            print(popup.ids)
            # print(popup.children.ids)
            popup.ids.plot_box.add_widget(plot_widget)
        popup.open()


        country=self.root.ids.country_city_input.ids.country_name.text
        print(country)
        df = pd.read_csv('country_voltage_data.csv')

        # Filter DataFrame based on country
        filtered_df = df[df['Country'].str.lower().str.contains(country.lower())]

        # Create a popup or layout to display information
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Check if filtered_df contains any rows
        if not filtered_df.empty:
            # Iterate through rows
            for index, row in filtered_df.iterrows():
                # Create labels with the appropriate data
                country_label = Label(text=f"Country: {row['Country']}", size_hint_y=None, height=40)
                single_phase_voltage_label = Label(text=f"Single Phase Voltage: {row['Single Phase Voltage']}",
                                                   size_hint_y=None, height=40)
                three_phase_voltage_label = Label(text=f"Three Phase Voltage: {row['Three Phase Voltage']}",
                                                  size_hint_y=None, height=40)
                frequency_label = Label(text=f"Frequency (Hz): {row['Frequency (Hz)']}", size_hint_y=None, height=40)

                # Add labels to the layout
                popup_layout.add_widget(country_label)
                popup_layout.add_widget(single_phase_voltage_label)
                popup_layout.add_widget(three_phase_voltage_label)
                popup_layout.add_widget(frequency_label)
        else:
            # Handle the case where no data is found
            no_data_label = Label(text="No data found for the selected country", size_hint_y=None, height=40)
            popup_layout.add_widget(no_data_label)

        # Add a close button
        close_button = Button(text="Close", size_hint_y=None, height=40)
        close_button.bind(on_release=lambda x: popup_electric.dismiss())
        popup_layout.add_widget(close_button)

        # Create and open the popup
        popup_electric = Popup(title='Country Details', content=popup_layout, size_hint=(0.8, 0.8))
        popup_electric.open()
        


if __name__ == '__main__':
    WeatherApp().run()
    print()
