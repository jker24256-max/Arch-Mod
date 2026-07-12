import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: container
    width: 640
    height: 480
    color: "#0B0C10"

    Image {
        id: bgImage
        source: config.background || "camo_red.jpg"
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
    }

    // Centered Login Card
    Rectangle {
        id: loginCard
        width: 350
        height: 280
        color: "#E61F2833" // Semi-transparent Carbon
        border.color: "#D90429" // Crimson border
        border.width: 1
        radius: 8
        anchors.centerIn: parent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15

            Text {
                text: "JKER OS // SYSTEM ACCESS"
                color: "#D90429"
                font.family: config.font || "Courier New"
                font.pixelSize: 16
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }

            // Username input
            TextField {
                id: user_input
                placeholderText: "Username"
                text: "jker" // Default auto-login user
                color: "#EDF2F4"
                font.family: config.font || "Courier New"
                Layout.fillWidth: true
                background: Rectangle {
                    color: "#151A21"
                    border.color: user_input.activeFocus ? "#D90429" : "#8D99AE"
                    border.width: 1
                    radius: 4
                }
            }

            // Password input
            TextField {
                id: password_input
                placeholderText: "Password"
                echoMode: TextInput.Password
                color: "#EDF2F4"
                font.family: config.font || "Courier New"
                Layout.fillWidth: true
                background: Rectangle {
                    color: "#151A21"
                    border.color: password_input.activeFocus ? "#D90429" : "#8D99AE"
                    border.width: 1
                    radius: 4
                }
            }

            Button {
                id: login_btn
                text: "AUTHENTICATE"
                Layout.fillWidth: true
                contentItem: Text {
                    text: login_btn.text
                    color: "#EDF2F4"
                    font.family: config.font || "Courier New"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: login_btn.hovered ? "#D90429" : "#1F2833"
                    border.color: "#D90429"
                    border.width: 1
                    radius: 4
                }
                onClicked: {
                    sddm.login(user_input.text, password_input.text, sessionModel.lastIndex)
                }
            }
        }
    }
}
