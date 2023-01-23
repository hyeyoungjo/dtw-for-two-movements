import pandas as pd


class WorkoutDataset:

    def __init__(self, warping_positions, analysis_positions):
        self.data = None
        self.mode_names = None
        self.data_by_mode = None
        self.analysis_variables = None
        self.warping_variables = None

        self.user_string = 'user_'
        self.expert_string = 'ref_'

        self.warping_positions = warping_positions
        self.analysis_positions = analysis_positions

    def load_data(self, file_path):
        self.data = pd.read_csv(file_path)
        self.mode_names = self.data["Mode"].unique()
        self.data_by_mode = {mode_name: self.data[self.data["Mode"] == mode_name] for mode_name in self.mode_names}

        self.index_warping_and_analysis_columns()

    def index_warping_and_analysis_columns(self):
        analysis_columns = []
        warping_columns = []

        for column in self.data.columns:
            is_relevant_warping = False
            for relevant_warping in self.warping_positions:
                if relevant_warping in column:
                    is_relevant_warping = True
                    break
            if is_relevant_warping and column.endswith('-X'):
                tracker_name = column[:-2]
                if tracker_name + "-Y" in self.data.columns and tracker_name + "-Z" in self.data.columns:
                    warping_columns += [tracker_name]

            is_relevant_analysis = False
            for relevant_analysis in self.analysis_positions:
                if relevant_analysis in column:
                    is_relevant_analysis = True
                    break
            if is_relevant_analysis and not column.endswith('-X') and not column.endswith('-Y') and not column.endswith('-Z'):
                analysis_columns += [column]

        self.warping_variables = []
        for column_name in warping_columns:
            if column_name.startswith(self.user_string):
                self.warping_variables += [column_name[len(self.user_string):]]

        self.analysis_variables = []
        for column_name in analysis_columns:
            if column_name.startswith(self.user_string):
                self.analysis_variables += [column_name[len(self.user_string):]]

    def select_column_names(self, time_warping_included=True, comparison_included=False):
        selected_columns = []

        if time_warping_included:
            for variable in self.warping_variables:
                for suffix in ['-X', '-Y', '-Z']:
                    selected_columns += ["{}{}".format(variable, suffix)]

        if comparison_included:
            for variable in self.analysis_variables:
                selected_columns += [variable]

        return selected_columns

    def compile_dataset(self, mode, selected_columns, from_user=True):
        mode_data = self.data_by_mode[mode]

        name_string = self.user_string if from_user else self.expert_string
        rename_dict = {}
        column_names = []

        for column_name in selected_columns:
            full_name = name_string + column_name
            column_names += [full_name]
            rename_dict[full_name] = column_name

        return mode_data[column_names].copy().reset_index(drop=True).rename(rename_dict, axis=1)