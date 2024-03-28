import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import calendar

def main():
    st.image("GDI.jpg", width=1050)
    st.sidebar.title("Instrucciones")
    st.sidebar.write("¡Bienvenido a la aplicación de gerenciamiento diario PQCDS!")
    st.sidebar.markdown("Por favor sigue las instrucciones paso a paso para utilizar la herramienta correctamente.")
    
    st.sidebar.markdown("### Pasos:")
    st.sidebar.markdown("- **Paso 1:** Ingresa el indicador clave.")
    st.sidebar.markdown("- **Paso 2:** Establece la meta para el indicador.")
    st.sidebar.markdown("- **Paso 3:** Define si el indicador es 'Mejor Menor' o 'Mejor Mayor'.")
    st.sidebar.markdown("- **Paso 4:** Ingresa el resultado diario para el indicador.")
    st.sidebar.markdown("- **Paso 5:** Observa el gráfico de control respecto a la meta.")
    st.sidebar.markdown("- **Paso 6:** Analiza el desempeño diario del indicador.")
    
    st.sidebar.markdown("### Información Adicional:")
    st.sidebar.markdown("👉 **Para más información: [LinkedIn](https://www.linkedin.com/in/josemaguilar/)**")
    
    st.sidebar.title("Configuración del Indicador Clave")
    indicator_name = st.sidebar.text_input("Nombre del Indicador:")
    target = st.sidebar.number_input("Meta:", step=0.01)
    is_better_lower = st.sidebar.radio("Mejor cuando:", ("Menor que la meta", "Mayor que la meta"))
    
    st.sidebar.subheader("Ingreso de Resultados Diarios")
    first_day_of_month_input = st.sidebar.date_input("Ingrese el primer día del mes:", value=datetime.now().replace(day=1))
    num_days_in_month = calendar.monthrange(first_day_of_month_input.year, first_day_of_month_input.month)[1]
    
    daily_results = []
    cause_columns = {}
    for day in range(1, num_days_in_month + 1):
        date = first_day_of_month_input.replace(day=day)
        day_of_week = date.strftime("%A")  # Obtener el nombre del día de la semana
        daily_result = st.sidebar.number_input(f"Ingrese el resultado del día {day} ({date.strftime('%d/%m/%Y')} - {day_of_week}):", step=0.01)
        daily_results.append(daily_result)
        
        if daily_result < target:
            cause_columns[day] = st.sidebar.selectbox(f"Causas para el día {day} ({date.strftime('%d/%m/%Y')} - {day_of_week}):", [" ","Materiales", "Métodos", "Maquinaria", "Mano de obra", "Medio ambiente", "Medición"])
    
    data_df = pd.DataFrame({"Día": [first_day_of_month_input.replace(day=day) for day in range(1, num_days_in_month + 1)], "Resultado": daily_results})

    # Agregar la columna de causas al DataFrame
    causas = []
    for day in range(1, num_days_in_month + 1):
        if day in cause_columns:
            causas.append(cause_columns[day])
        else:
            causas.append(None)  # Opcional: Puedes cambiar None por un valor por defecto si prefieres
    data_df["Causas"] = causas
    
    st.subheader("Seguimiento diario")
    if not data_df.empty:
        # Calcula el máximo entre el máximo valor registrado y la meta
        max_value = max(data_df["Resultado"].max(), target)
        
        # Calcula la media de los resultados excluyendo los valores en cero
        non_zero_results = data_df[data_df["Resultado"] != 0]["Resultado"]
        mean_result = non_zero_results.mean() if not non_zero_results.empty else 0
        
        # Determine el cumplimiento de la meta
        if is_better_lower == "Menor que la meta":
            cumplimiento = mean_result <= target
        else:
            cumplimiento = mean_result >= target
        
        # Crea el Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = mean_result,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Media del Indicador ({indicator_name})"},
            gauge = {'axis': {'range': [None, max_value]},
                     'bar': {'color': "red" if cumplimiento else "green"},
                     'steps' : [
                         {'range': [0, target], 'color': "lightblue"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target}}))

        fig_gauge.update_layout(height=450, width=250)
        
        # Gráfico de Control respecto a la Meta
        if not non_zero_results.empty:
            # Determine el cumplimiento de la meta
            if is_better_lower == "Menor que la meta":
                data_df["Cumplimiento"] = data_df["Resultado"] >= target
            else:
                data_df["Cumplimiento"] = data_df["Resultado"] <= target
            
            # Filtrar los puntos que no sean 0
            data_df_filtered = data_df[data_df["Resultado"] != 0]
            
            # Cambie el color de los puntos en el gráfico según si se cumple o no la meta
            colors = ['red' if cumplimiento else 'green' for cumplimiento in data_df_filtered["Cumplimiento"]]
            
            # Gráfico de puntos
            fig_control = go.Figure()
            fig_control.add_trace(go.Scatter(x=data_df_filtered["Día"], y=data_df_filtered["Resultado"], mode='markers', marker=dict(color=colors, size=10), name='Resultado Diario'))
            
            # Línea de meta
            fig_control.add_hline(y=target, line_dash="dash", line_color="black", annotation_text="Meta", annotation_position="top right")
            
            # Gráfico de líneas
            fig_control.add_trace(go.Scatter(x=data_df_filtered["Día"], y=data_df_filtered["Resultado"], mode='lines', line=dict(color='blue'), name='Tendencia Diaria'))
            
            fig_control.update_layout(title=f'Gráfico de Control de {indicator_name}',
                              xaxis_title='Día',
                              yaxis_title='Resultado')
        
        # Mostrar los gráficos en las columnas
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_gauge)
        with col2:
            if not non_zero_results.empty:
                st.plotly_chart(fig_control)
            else:
                st.write("No hay suficientes datos para mostrar el gráfico de control.")
    
    st.subheader("Causas frecuentes y días con mayores desvíos")
    if not data_df.empty:
        col3, col4 = st.columns(2)
        
        # Graficar las causas con mayor frecuencia
        if "Causas" in data_df.columns:
            causas_filtradas = data_df[data_df["Resultado"] != 0]["Causas"].value_counts().sort_values(ascending=False)
            if not causas_filtradas.empty:
                fig_causas = go.Figure(go.Bar(
                    x=causas_filtradas.values,
                    y=causas_filtradas.index,
                    orientation='h'
                ))
                fig_causas.update_layout(title='Causas de desviaciones',
                                          xaxis_title='Frecuencia',
                                          yaxis_title='Causas',
                                          yaxis=dict(autorange="reversed"))
                fig_causas.update_layout(height=450, width=250)
                with col3:
                    st.plotly_chart(fig_causas)
        
        # Create calendar plot
        # Preparar los datos para el gráfico de calendario
        calendar_data = {}
        for i, row in data_df.iterrows():
            week_of_year = row['Día'].isocalendar()[1]
            if week_of_year not in calendar_data:
                calendar_data[week_of_year] = [None] * 7
            day_of_week = row['Día'].weekday()
            if row['Resultado'] == 0:
                calendar_data[week_of_year][day_of_week] = None  # Valor en blanco
            elif row['Resultado'] < target and is_better_lower == "Menor que la meta":
                calendar_data[week_of_year][day_of_week] = 1  # Valor en verde
            elif row['Resultado'] > target and is_better_lower == "Mayor que la meta":
                calendar_data[week_of_year][day_of_week] = 1   # Valor en verde
            else:
                calendar_data[week_of_year][day_of_week] = -1  # Valor en rojo
        
        fig_calendar = go.Figure()
        for week_of_year, data in calendar_data.items():
            fig_calendar.add_trace(go.Heatmap(
                z=[data],
                x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                y=[f'Semana {week_of_year}'],
                colorscale=[[0, 'red'], [0.5, 'white'], [1, 'green']],  # Personaliza la escala de colores
                zmin=-1,  # Valor mínimo personalizado
                zmax=1,   # Valor máximo personalizado
            ))

        fig_calendar.update_layout(title=f'{indicator_name} - Calendario de Resultados',
                                   xaxis_title='Día de la Semana',
                                   yaxis_title='Semana del Año',
                                   yaxis=dict(autorange="reversed"),
                                   yaxis_showticklabels=False)  # Oculta los nombres de las semanas en el eje Y

        with col4:
            st.plotly_chart(fig_calendar)

    st.subheader('Datos ingresados')
    st.write(data_df)

if __name__ == "__main__":
    main()

