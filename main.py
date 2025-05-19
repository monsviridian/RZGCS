from backend.parameter_model import ParameterTableModel

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    sensor_model = SensorViewModel()
    logger = Logger()
    parameter_model = ParameterTableModel()
    serial_connector = SerialConnector(sensor_model, logger, parameter_model)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("sensorModel", sensor_model)
    engine.rootContext().setContextProperty("serialConnector", serial_connector)
    engine.rootContext().setContextProperty("parameterModel", parameter_model) 