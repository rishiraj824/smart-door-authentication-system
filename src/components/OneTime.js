import React, { Component } from 'react';
import OtpInput from 'react-otp-input';
import "./OneTime.css";
import {
  useLocation, withRouter
} from "react-router-dom";
 
class OneTime extends Component {
  state = { 
    otp: '' ,
    status: false,
    message:""
};
  
  // useQuery = () => {
  //   return new URLSearchParams(useLocation().search);
  // }
  
  // const query = useQuery();
  handleOtpChange = otp => {
    this.setState({ otp });
  };
  handleSubmit(event) {
    if (this.state.otp.length==6){
      const faceId = new URLSearchParams(this.props.location.search).get('faceId');
      const url =
        "https://02xohgtag5.execute-api.us-west-2.amazonaws.com/prod/otp-verification";
    
      const data = {
        otp: this.state.otp,
        faceId
      };
      console.log("Data is", data)
      fetch(url, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
          "Content-Type" : "application/json",
              "Access-Control-Allow-Headers" : "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
              "Access-Control-Allow-Methods" : "OPTIONS,POST",
              "Access-Control-Allow-Credentials" : true,
              "Access-Control-Allow-Origin" : "*",
              "X-Requested-With" : "*"
        },
      })
        .then((res) => res.json())
        .catch((error) => console.error("Error:", error))
        .then((response) => {
          this.setState({status: true})
          console.log("Success:", JSON.parse(response.body))
          this.setState({message: JSON.parse(response.body).message})
        });
    this.setState({otp:""})
      }
  }
  render() {
    let InputOrText;
    if (this.state.status === true){
      InputOrText = <div>{this.state.message}</div>;
    }
    else{
      InputOrText = null;
            }
      console.log(InputOrText)
    return (

      <React.Fragment>
        <div className="view">
          <div className="card">
            <form onSubmit={this.handleSubmit}>
              <p>Enter verification code</p>
              <div className="margin-top--small">
              <OtpInput
              inputStyle="inputStyle"
              numInputs={6}
              isDisabled={false}
              hasErrored={false}
              errorStyle="error"
              onChange={this.handleOtpChange}
              separator={<span>-</span>}
              isInputNum={true}
              isInputSecure={false}
              shouldAutoFocus
              value={this.state.otp}
              placeholder={123456}
            />
  
              </div>
              <p>{InputOrText}</p>
              <div className="btn-row">
                <button
                  className="btn-primary btn margin-top--large"
                  type="button"
                  onClick={()=>this.handleSubmit()}
                >
                  Proceed
              </button>
              </div>
            </form>
          </div>
        </div>
      </React.Fragment>
      
    );
  }
}

export default withRouter(OneTime);