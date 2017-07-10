from bokeh.plotting import figure
from bokeh.io import output_file, show

fg = figure(x_axis_label="x_axis", y_axis_label="y_axis", tools='box_select, lasso_select')

x = [x for x in range(20)]
y = [y for y in range(23)]

fg.line(x, y, line_width=4)
fg.circle(x, y, size=5, fill_color='white')

output_file("sample_plot.html")
show(fg)

