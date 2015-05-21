'use strict';

var _get = function get(object, property, receiver) { var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ('value' in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _classCallCheck = function (instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } };

var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ('value' in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

var _inherits = function (subClass, superClass) { if (typeof superClass !== 'function' && superClass !== null) { throw new TypeError('Super expression must either be null or a function, not ' + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) subClass.__proto__ = superClass; };

var OptionButton = (function (_React$Component) {
  function OptionButton() {
    _classCallCheck(this, OptionButton);

    if (_React$Component != null) {
      _React$Component.apply(this, arguments);
    }
  }

  _inherits(OptionButton, _React$Component);

  _createClass(OptionButton, [{
    key: 'update',
    value: function update() {
      this.props.toggleState(this.props.option.code);
    }
  }, {
    key: 'render',
    value: function render() {
      var option = this.props.option;
      var cx = React.addons.classSet;

      var classes = cx({
        options_button: true,
        disabled: !this.props.option.value
      });

      return React.createElement(
        'div',
        { className: classes, onClick: this.update.bind(this) },
        option.description
      );
    }
  }]);

  return OptionButton;
})(React.Component);

var OptionsField = (function (_React$Component2) {
  function OptionsField() {
    _classCallCheck(this, OptionsField);

    if (_React$Component2 != null) {
      _React$Component2.apply(this, arguments);
    }
  }

  _inherits(OptionsField, _React$Component2);

  _createClass(OptionsField, [{
    key: 'update',
    value: function update(event) {
      this.props.setOptions(event.target.value);
    }
  }, {
    key: 'getCodes',
    value: function getCodes(options) {
      var output = '';
      options.filter(function (item) {
        return item.value;
      }).forEach(function (item) {
        return output += item.code;
      });

      return output;
    }
  }, {
    key: 'render',
    value: function render() {
      var options = this.props.options;

      return React.createElement('input', { type: 'text', onChange: this.update.bind(this), value: this.getCodes(options) });
    }
  }]);

  return OptionsField;
})(React.Component);

var WhisperOptions = (function (_React$Component3) {
  function WhisperOptions(props) {
    _classCallCheck(this, WhisperOptions);

    _get(Object.getPrototypeOf(WhisperOptions.prototype), 'constructor', this).call(this, props);
    this.state = {
      options: [{
        description: 'Encrypt',
        code: 'e',
        value: true
      }, {
        description: 'Email',
        code: 'm',
        value: true
      }, {
        description: 'Expire',
        code: 'x',
        value: true
      }, {
        description: 'Disposable',
        code: 'd',
        value: false
      }, {
        description: 'Owner',
        code: 'o',
        value: false
      }, {
        description: 'Two-Factor',
        code: 't',
        value: false
      }]
    };
  }

  _inherits(WhisperOptions, _React$Component3);

  _createClass(WhisperOptions, [{
    key: 'toggleButtonState',
    value: function toggleButtonState(code) {
      var options = this.state.options;

      options.forEach(function (item) {
        if (item.code == code) {
          item.value = !item.value;
        }
      });

      this.setState({
        options: options
      });
    }
  }, {
    key: 'updateFromField',
    value: function updateFromField(value) {
      console.log('Update called');
      console.log('Value: ' + value);

      var options = this.state.options;

      options.forEach(function (item) {
        if (value.indexOf(item.code) != -1) {
          item.value = true;
        } else {
          item.value = false;
        }
      });

      this.setState({
        options: options
      });
    }
  }, {
    key: 'render',
    value: function render() {
      var _this = this;

      return React.createElement(
        'div',
        null,
        this.state.options.map(function (option) {
          return React.createElement(OptionButton, { option: option, toggleState: _this.toggleButtonState.bind(_this) });
        }),
        React.createElement(OptionsField, { setOptions: this.updateFromField.bind(this), options: this.state.options })
      );
    }
  }]);

  return WhisperOptions;
})(React.Component);

React.render(React.createElement(WhisperOptions, null), document.getElementById('react_test'));