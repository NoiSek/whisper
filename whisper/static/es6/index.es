class OptionButton extends React.Component {
  update() {
    this.props.toggleState(this.props.option.code);
  }

  render() {
    let option = this.props.option;
    let cx = React.addons.classSet;
    
    let classes = cx({
      'options_button': true,
      'disabled': !this.props.option.value
    });

    return (
      <div className={classes} onClick={this.update.bind(this)}>{option.description}</div>
    );
  }
}

class OptionsField extends React.Component {
  update(event) {
    this.props.setOptions(event.target.value);
  }

  getCodes(options) {
    let output = "";
    options.filter(item => item.value).forEach(item => output += item.code);

    return output;
  }

  render() {
    let options = this.props.options;

    return(
      <input type="text" onChange={this.update.bind(this)} value={this.getCodes(options)} />
    );
  }
}

class WhisperOptions extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      "options": [
        {
          "description": "Encrypt",
          "code": "e",
          "value": true
        },
        {
          "description": "Email",
          "code": "m",
          "value": true
        },
        {
          "description": "Expire",
          "code": "x",
          "value": true
        },
        {
          "description": "Disposable",
          "code": "d",
          "value": false
        },
        {
          "description": "Owner",
          "code": "o",
          "value": false
        },
        {
          "description": "Two-Factor",
          "code": "t",
          "value": false
        }
      ]
    };
  }

  toggleButtonState(code) {
    let options = this.state.options;

    options.forEach(item => {
      if(item.code == code) {
        item.value = !item.value;
      }
    });

    this.setState({
      "options": options
    });
  }

  updateFromField(value) {
    console.log("Update called");
    console.log("Value: " + value);
    
    let options = this.state.options;

    options.forEach(item => {
      if(value.indexOf(item.code) != -1) {
        item.value = true;
      }

      else {
        item.value = false;
      }
    });

    this.setState({
      "options": options
    });
  }

  render() {
    return (
      <div>
        {this.state.options.map(option => <OptionButton option={option} toggleState={this.toggleButtonState.bind(this)} />)}
        <OptionsField setOptions={this.updateFromField.bind(this)} options={this.state.options}></OptionsField>
      </div>
    );
  }
}

React.render(
  <WhisperOptions />, 
  document.getElementById("react_test")
);