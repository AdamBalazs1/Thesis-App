import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd


class PlotTool:
    def __init__(self, frame, db_path, instruction_dict):
        self.frame = frame
        self.db_path = db_path
        self.instruction = instruction_dict
        self.graph_type = instruction_dict.get("type", "").lower()
        self.table = instruction_dict.get("table")
        self.columns = instruction_dict.get("columns", {})
        self.canvas = None

        print(self.db_path, self.instruction, self.graph_type, self.table, self.columns, sep="\n")

    def build(self):
        data = self._fetch_data()
        if not data:
            return

        fig = self._plot(data)

        if fig:
            self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)


    def _fetch_data(self):
        # Looks good
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cols = [col for col in self.columns.values() if col]
            if not cols:
                return None

            col_str = ", ".join(cols)
            cur.execute(f"SELECT {col_str} FROM {self.table}")
            data = cur.fetchall()
            conn.close()
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def _plot(self, data):
        # This also look good
        if self.graph_type == "pie":
            return self._plot_pie(data)
        elif self.graph_type == "bar":
            return self._plot_bar(data)
        elif self.graph_type == "line":
            return self._plot_line(data)
        elif self.graph_type == "top5_inventory_cost":
            return self._plot_top5(data)
        elif self.graph_type == "inventory_turnover_ratio":
            return self._plot_itr(data)
        elif self.graph_type == "backlog":
            return self._plot_backlog(data)
        else:
            print(f"Unknown graph type: {self.graph_type}")
            return None

    def _plot_pie(self, data):
        labels = [row[0] for row in data]
        values = [row[1] for row in data]

        fig = plt.Figure(figsize=(1, 1), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title("Pie Chart")
        return fig

    def _plot_bar(self, data):
        labels = [row[0] for row in data]
        values1 = [row[1] for row in data]
        values2 = [row[2] for row in data] if len(data[0]) > 2 else None

        fig = plt.Figure(figsize=(1, 1), dpi=100)
        ax = fig.add_subplot(111)
        x = range(len(labels))
        ax.bar(x, values1, label=self.columns.get("col_2", "Series 1"))

        if values2:
            ax.bar(x, values2, bottom=values1, label=self.columns.get("col_3", "Series 2"))

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.set_title("Bar Chart")
        return fig

    def _plot_line(self, data):
        labels = [row[0] for row in data]
        values = [row[1] for row in data]
        print("labels: ", labels)
        print("values: ", values)

        fig = plt.Figure(figsize=(1, 1), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(labels, values, marker="o")
        ax.set_title("Line Chart")
        ax.set_xlabel(self.columns.get("col_1", "X"))
        ax.set_ylabel(self.columns.get("col_2", "Y"))
        return fig

    def _plot_top5(self, data):
        mat_totals = {}
        for row in data:
            mat_id, qty, cost = row
            mat_totals[mat_id] = mat_totals.get(mat_id, 0) + (qty * cost)

        top5 = sorted(mat_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        labels, values = zip(*top5)

        fig = plt.Figure(figsize=(1, 1), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title("Top 5 Inventory Cost")
        return fig

    def _plot_itr(self, data):
        months = [row[0] for row in data]
        cogs = [row[1] for row in data]
        aic = [row[2] for row in data]

        itr = [c / a if a != 0 else 0 for c, a in zip(cogs, aic)]

        fig = plt.Figure(figsize=(1, 1), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(months, itr, marker="o")
        ax.set_title("Inventory Turnover Ratio")
        ax.set_xlabel("Month")
        ax.set_ylabel("ITR")
        return fig

    def _plot_backlog(self, data):
        df = pd.DataFrame(data, columns=["line", "month", "qty"])
        pivot = df.pivot(index="month", columns="line", values="qty")

        fig = plt.Figure(figsize=(1, 1), dpi=100)
        ax = fig.add_subplot(111)
        pivot.plot(kind="bar", ax=ax)
        ax.set_title("Production Backlog")
        ax.set_xlabel("Month")
        ax.set_ylabel("Backlog (Qty)")
        return fig

    def destroy(self):
        self.canvas.get_tk_widget().destroy()

if __name__ == '__main__':
   pass