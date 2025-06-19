"""
Unit-Tests für das Parameter-Model.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from PySide6.QtCore import Qt, QModelIndex

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Module importieren
from backend.parameter_model import ParameterTableModel

class TestParameterTableModel:
    """Test-Suite für die ParameterTableModel-Klasse."""
    
    @pytest.fixture
    def model(self):
        """Fixture für ein frisches ParameterTableModel."""
        return ParameterTableModel()
    
    @pytest.fixture
    def sample_params(self):
        """Fixture mit Beispielparametern."""
        return [
            {
                'name': 'RATE_RLL_P',
                'value': '0.15',
                'default': '0.1',
                'unit': '',
                'options': [],
                'description': 'Roll rate control P gain'
            },
            {
                'name': 'RATE_PIT_P',
                'value': '0.15',
                'default': '0.1',
                'unit': '',
                'options': [],
                'description': 'Pitch rate control P gain'
            },
            {
                'name': 'RATE_YAW_P',
                'value': '0.2',
                'default': '0.15',
                'unit': '',
                'options': [],
                'description': 'Yaw rate control P gain'
            }
        ]
    
    def test_initialization(self, model):
        """Testet die korrekte Initialisierung des Models."""
        # Assert
        assert model._params == []
        assert model.rowCount() == 0
    
    def test_set_parameters(self, model, sample_params):
        """Testet das Setzen von Parametern im Model."""
        # Act
        with patch.object(model, 'beginResetModel') as mock_begin:
            with patch.object(model, 'endResetModel') as mock_end:
                with patch.object(model, 'parametersLoaded') as mock_signal:
                    model.set_parameters(sample_params)
        
        # Assert
        assert model._params == sample_params
        assert model.rowCount() == 3
        mock_begin.assert_called_once()
        mock_end.assert_called_once()
        mock_signal.emit.assert_called_once()
    
    def test_rowCount(self, model, sample_params):
        """Testet die rowCount-Methode."""
        # Arrange
        model.set_parameters(sample_params)
        
        # Act & Assert
        assert model.rowCount() == 3
        assert model.rowCount(QModelIndex()) == 3
    
    def test_data_valid_index(self, model, sample_params):
        """Testet die data-Methode mit gültigen Indizes."""
        # Arrange
        model.set_parameters(sample_params)
        
        # Act & Assert - Verschiedene Rollen testen
        index = model.index(0, 0)
        assert model.data(index, ParameterTableModel.NameRole) == 'RATE_RLL_P'
        assert model.data(index, ParameterTableModel.ValueRole) == '0.15'
        assert model.data(index, ParameterTableModel.DefaultValueRole) == '0.1'
        assert model.data(index, ParameterTableModel.UnitRole) == ''
        assert model.data(index, ParameterTableModel.OptionsRole) == []
        assert model.data(index, ParameterTableModel.DescRole) == 'Roll rate control P gain'
    
    def test_data_invalid_index(self, model, sample_params):
        """Testet die data-Methode mit ungültigen Indizes."""
        # Arrange
        model.set_parameters(sample_params)
        
        # Act & Assert
        invalid_index = model.index(10, 0)  # Ungültiger Index
        assert model.data(invalid_index, ParameterTableModel.NameRole) is None
        
        # Ungültige Rolle
        valid_index = model.index(0, 0)
        assert model.data(valid_index, 999) is None
    
    def test_roleNames(self, model):
        """Testet die roleNames-Methode."""
        # Act
        roles = model.roleNames()
        
        # Assert
        expected_roles = {
            ParameterTableModel.NameRole: b'name',
            ParameterTableModel.ValueRole: b'value',
            ParameterTableModel.DefaultValueRole: b'defaultValue',
            ParameterTableModel.UnitRole: b'unit',
            ParameterTableModel.OptionsRole: b'options',
            ParameterTableModel.DescRole: b'description'
        }
        
        for role, name in expected_roles.items():
            assert roles[role] == name
    
    def test_set_parameter_value(self, model, sample_params):
        """Testet das Setzen eines einzelnen Parameterwerts."""
        # Arrange
        model.set_parameters(sample_params)
        
        # Mock das Signal
        with patch.object(model, 'parameterChanged') as mock_signal:
            with patch.object(model, 'dataChanged') as mock_dataChanged:
                # Act
                model.set_parameter_value('RATE_RLL_P', '0.2')
                
                # Assert
                assert model._params[0]['value'] == '0.2'
                mock_signal.emit.assert_called_once_with('RATE_RLL_P', '0.2')
                mock_dataChanged.emit.assert_called_once()
    
    def test_set_parameter_value_nonexistent(self, model, sample_params):
        """Testet das Setzen eines nicht existierenden Parameters."""
        # Arrange
        model.set_parameters(sample_params)
        
        # Act & Assert
        with patch.object(model, 'parameterChanged') as mock_signal:
            model.set_parameter_value('NONEXISTENT', '1.0')
            mock_signal.emit.assert_not_called()
            # Der Wert sollte nicht gesetzt werden, da der Parameter nicht existiert
            assert all(param['name'] != 'NONEXISTENT' for param in model._params)
    
    def test_get_parameter_value(self, model, sample_params):
        """Testet das Abrufen eines Parameterwerts."""
        # Arrange
        model.set_parameters(sample_params)
        
        # Act & Assert
        assert model.get_parameter_value('RATE_RLL_P') == '0.15'
        assert model.get_parameter_value('NONEXISTENT') is None
