import time

SCRIPT_ROOT = ""


class Tools:
    def get_time_diff(self, time_format, n_time: float) -> list:
        import time
        dif = time.time() - n_time
        t = Tools()
        days = t.num_formatting(dif / 60 ** 2 / 24, 3)
        hours = t.num_formatting(dif / 60 ** 2, 2)
        minutes = t.num_formatting(dif / 60, 2)
        seconds = int(dif)
        match time_format:
            case 'all':
                times = [days, hours, minutes, seconds]
                return times
            case 's':
                return seconds
            case 'm':
                return minutes
            case 'h':
                return hours
            case 'd':
                return days

    def format_timestamp(self, n_time):
        import time
        return time.strftime("%d %b %Y %H:%M", n_time)

    def error_message(self, error_name: str, description: str):
        print(f'!{error_name.upper()}: {description}!')

    def num_formatting(self, num, digits=0):
        return round(num, digits)

    def user_input(self, command_name="", command_mode=False):
        if not command_mode:
            response = input(': ')
        else:
            response = input(f'{command_name}-> ')
        return response.strip()

    def add_new_command(self):
        import json
        command = input().split(';')
        command_path = SCRIPT_ROOT + "commands.json"
        if len(command) == 4:
            with open(command_path, 'r') as f:
                data = f.read()
                commands = json.loads(data)
            for i in range(len(command)):
                command[i] = command[i].strip()
            new_command = {"name": command[0], "description": command[1], "format": command[2], "example": command[3]}
            commands.append(new_command)
            with open(command_path, 'w') as f:
                json.dump(commands, f)

    def get_event_id(self, command_name):
        try:
            event_id = int(self.user_input(command_name, True))
            return event_id
        except ValueError:
            Tools().error_message("Value Error", 'id must be integer')
            return -1


class App:
    def __init__(self):
        pass


class ConsoleApp:
    def __init__(self, add_cmd=False):
        self.add_cmd = add_cmd
        while add_cmd:
            Tools().add_new_command()
        self.show_table()
        while True:
            response = Tools().user_input()
            match response:
                case "events":
                    self.show_table()
                case "exit":
                    break
                case "add":
                    self.add_event()
                case "late_add":
                    self.late_add()
                case "timestamps":
                    self.show_timestamps()
                case "reset":
                    self.reset_time()
                case "edit":
                    self.edit_event()
                case 'delete':
                    self.delete_event()
                case "help":
                    Help().show_table()
                case _:
                    print('type "Help" for list of commands')

    def edit_event(self):
        Help().format_help("edit")
        user_input = Tools().user_input('edit', True).split(',')
        if len(user_input) != 3:
            Tools().error_message("wrong format", "too many parameters")
        event_id, new_name, new_description = user_input
        try:
            event_id = int(event_id)
        except ValueError:
            Tools().error_message("Value Error", 'id must be integer')
            return
        events = Configuration().load_events()
        events[event_id].set_name(new_name)
        events[event_id].set_description(new_description)
        Configuration().change_event(events[event_id], event_id)

    def show_timestamps(self):
        Help().format_help('timestamps')
        event_id = Tools().get_event_id("timestamps")
        if event_id == -1:
            return
        events = Configuration().load_events()
        time_stamps = events[event_id].get_timestamps()

        for i in range(len(time_stamps)):
            print(f"{i + 1}) {Tools().format_timestamp(time.localtime(time_stamps[i]))}")

    def reset_time(self):
        Help().format_help("reset")
        event_id = Tools().get_event_id("reset")
        if event_id == -1:
            return

        events = Configuration().load_events()
        events[event_id].reset_time()
        Configuration().change_event(events[event_id], event_id)

    def delete_event(self):
        Help().format_help("delete")
        try:
            event_id = int(Tools().user_input('delete', True))
        except ValueError:
            Tools().error_message("Value Error", 'id must be integer')
            return
        Configuration().delete_event(event_id)

    def show_table(self):
        from prettytable import PrettyTable
        table = PrettyTable()
        events = Configuration().load_events()
        table.field_names = ['Id', 'Name', 'Description', 'Reset Counter', 'Days Without', 'Hours Without', 'Minutes Without', 'Seconds Without', 'Last Time']

        if events is not None:
            for i in range(len(events)):
                event = events[i]
                start_time = event.get_start_time()
                if event.get_counter() != 0:
                    start_time = event.get_timestamps()[-1]

                days, hours, minutes, seconds = Tools().get_time_diff('all', start_time)
                timestamp = Tools().format_timestamp(time.localtime(start_time))
                # timestamps = []
                #
                # event_timestamps_start = len(event.get_timestamps()) - 1
                # for j in range(event_timestamps_start, 0, -1):
                #     if j == event_timestamps_start or j == event_timestamps_start - 1:
                #         timestamp = Tools().format_timestamp(time.localtime(event.get_timestamps()[j]))
                #         timestamps.append(timestamp)

                table.add_row([i, event.get_name(), event.get_description(), event.get_counter(), days, hours, minutes, seconds, timestamp])
        print()
        print(table)

    def add_event(self):
        Help().format_help('add')
        user_input = Tools().user_input('add', True)
        user_input = user_input.strip().split(',')
        if len(user_input) > 2:
            Tools().error_message("wrong format", "too many parameters")
        try:
            new_event = Event(user_input[0], user_input[1])
        except IndexError:
            Tools().error_message("Index error", 'not enough parameters')
            return
        Configuration().save_event(new_event)

        # event_name description

    def late_add(self):
        Help().format_help("late_add")
        user_input = Tools().user_input('late_add', True).split(',')
        if len(user_input) != 2:
            Tools().error_message("wrong format", "Wrong amount of parameters")
        event_id, new_timestamp = user_input
        try:
            event_id = int(event_id)
        except ValueError:
            Tools().error_message("Value Error", 'Id must be integer')
            return
        try:
            new_timestamp = time.mktime(time.strptime(new_timestamp.strip(), "%d %b %Y %H:%M"))
        except ValueError:
            Tools().error_message("Value Error", "Timestamp is in wrong format, format must be: %d %b %Y %H:%M. Make sure that you don't write 'September' instead of 'Sep'")
            return
        events = Configuration().load_events()
        Configuration().change_event(events[event_id], event_id, True, new_timestamp)


class Help:
    def __init__(self):
        import json
        command_path = SCRIPT_ROOT + "commands.json"
        with open(command_path, 'r') as f:
            commands_json = f.read()
            commands_json = json.loads(commands_json)
        self.commands_json = commands_json

    def show_table(self):
        from prettytable import PrettyTable
        table = PrettyTable()
        table.field_names = ['Id', 'Name', 'Description', 'Format', 'Format example']
        for i in range(len(self.commands_json)):
            command = self.commands_json[i]
            table.add_row([i, command['name'], command['description'], command['format'], command['example']])
        print(table)

    def format_help(self, command_name):
        found_format = self.get_format(command_name)
        if found_format != '':
            print(f"COMMAND FORMAT: {found_format}")

    def get_format(self, command_name):
        command_names = []
        for i in self.commands_json:
            command_names.append(i['name'])
        if command_names.count(command_name) != 0:
            command_index = command_names.index(command_name)
            return self.commands_json[command_index]['format']
        return ''


class Event:
    def __init__(self, name, description, start_time=-1, counter=0, time_stamps=None, get_counter_from_len=False):
        if time_stamps is None:
            time_stamps = []
        import time

        self.name = name
        self.description = description
        self.start_time = start_time
        self.counter = counter
        self.timestamps = time_stamps
        if get_counter_from_len:
            self.counter = len(time_stamps)
        if start_time == -1:
            self.start_time = time.time()

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_start_time(self):
        return self.start_time

    def get_counter(self):
        return self.counter

    def get_timestamps(self):
        return self.timestamps

    def reset_time(self):
        import time
        self.timestamps.append(self.start_time)
        self.counter = len(self.timestamps)
        self.start_time = time.time()


class Configuration:
    def __init__(self):
        self.filename = SCRIPT_ROOT + '/events.json'

    def is_empty(self, filename, raise_empty_message=True):
        with open(filename, 'r') as f:
            data = f.read()
            if data == "[]" or data == "":
                if raise_empty_message:
                    print("!Events aren't found!")
                return True
            return False

    def load_events(self) -> list:
        import json
        try:
            with open(self.filename, 'r') as f:
                data = f.read()
        except FileNotFoundError:
            Tools().error_message("File Not Found Error", "You don't have events file, creating...")
            open(self.filename, 'x')
            return

        if self.is_empty(self.filename):
            return

        json_extraction = json.loads(data)
        events = []
        for i in range(len(json_extraction)):
            event = json_extraction[i][str(i)]
            # print(len(event['time_stamps']))
            events.append(Event(event['name'], event['description'], event['start_time'], event['counter'], event['time_stamps'], True))
        return events

    def new_event(self, event_id, name, description, start_time, counter, time_stamps):
        return {f"{event_id}": {"name": name, "description": description, "start_time": start_time, "counter": counter, "time_stamps": time_stamps}}

    def save_event(self, event: Event, is_late_save=False, timestamp=0):

        import json
        with open(self.filename, 'r') as f:
            data = f.read()
            amount_of_events = 0
            events = []
            if not self.is_empty(self.filename, False):
                events = json.loads(data)
                amount_of_events = len(events)

        # new_event = {f"{amount_of_events}": {"name": event.get_name(), "description": event.get_description(), "startTime": event.get_start_time(), "counter": event.get_counter()}}

        new_event = Configuration().new_event(amount_of_events, event.get_name(), event.get_description(), event.get_start_time(), event.get_counter(), event.get_timestamps())
        events.append(new_event)
        with open(self.filename, 'w') as f:
            json.dump(events, f)

    def change_event(self, event, event_id, is_late_save=False, timestamp=0):
        if self.is_empty(self.filename):
            return

        import json
        with open(self.filename, 'r') as f:
            data = f.read()
            events = json.loads(data)
        timestamps = event.get_timestamps()
        if is_late_save:
            timestamps.append(timestamp)
            timestamps = sorted(timestamps)

        new_event = Configuration().new_event(event_id, event.get_name(), event.get_description(), event.get_start_time(), event.get_counter(), timestamps)

        events[event_id] = new_event

        with open(self.filename, 'w') as f:
            json.dump(events, f)

    def delete_event(self, event_id):
        if self.is_empty(self.filename):
            return
        import json
        with open(self.filename, 'r') as f:
            data = f.read()
            events = json.loads(data)
        for i in range(event_id + 1, len(events)):
            events[i][str(i - 1)] = events[i].pop(str(i))
        try:
            events.pop(event_id)
        except IndexError:
            Tools().error_message("Index Error", "Wrong Id")
        with open(self.filename, 'w') as f:
            json.dump(events, f)


ConsoleApp()
