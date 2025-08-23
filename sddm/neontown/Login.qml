import "components"

import QtQuick 2.0
import QtQuick.Layouts 1.2

import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import Qt5Compat.GraphicalEffects
import org.kde.kirigami 2.20 as Kirigami

SessionManagementScreen {

    property bool showUsernamePrompt: !showUserList

    property string lastUserName

    //the y position that should be ensured visible when the on screen keyboard is visible
    property int visibleBoundary: mapFromItem(loginButton, 0, 0).y
    //onHeightChanged: visibleBoundary = mapFromItem(loginButton, 0, 0).y + loginButton.height + units.smallSpacing

    signal loginRequest(string username, string password)

    onShowUsernamePromptChanged: {
        if (!showUsernamePrompt) {
            lastUserName = ""
        }
    }

    /*
    * Login has been requested with the following username and password
    * If username field is visible, it will be taken from that, otherwise from the "name" property of the currentIndex
    */
    function startLogin() {
        var username = userList.selectedUser
        var password = passwordBox.text

        //this is partly because it looks nicer
        //but more importantly it works round a Qt bug that can trigger if the app is closed with a TextField focussed
        //See https://bugreports.qt.io/browse/QTBUG-55460
        loginButton.forceActiveFocus();
        loginRequest(username, password);
    }

    ColumnLayout {
        id: userAndPassword
        Layout.alignment: Qt.AlignHCenter
        Layout.fillWidth: true
        spacing: 6

        RowLayout{
            id: passwordRow
            Layout.fillWidth: true

            PlasmaComponents.TextField {
                id: passwordBox
                Layout.fillWidth: true
                placeholderText: i18nd("plasma_lookandfeel_org.kde.lookandfeel", "Password")
                focus: !showUsernamePrompt || lastUserName
                echoMode:  TextInput.Password
                horizontalAlignment: TextInput.Center
                onAccepted: startLogin()
                color: config.stringValue("passwordTextColor")
                Keys.onEscapePressed: {
                    mainStack.currentItem.forceActiveFocus();
                }

                //if empty and left or right is pressed change selection in user switch
                //this cannot be in keys.onLeftPressed as then it doesn't reach the password box
                Keys.onPressed: event => {
                    if (event.key == Qt.Key_Left && !text) {
                        userList.decrementCurrentIndex();
                        event.accepted = true
                    }
                    if (event.key == Qt.Key_Right && !text) {
                        userList.incrementCurrentIndex();
                        event.accepted = true
                    }
                }

                Connections {
                    target: sddm
                    function onLoginFailed() {
                        passwordBox.selectAll()
                        passwordBox.forceActiveFocus()
                    }
                }

                background: Rectangle {
                    opacity: 0
                    radius: 1
                    color: "transparent"
                }

            }
            Rectangle{
                width:  12
                height: 12
                border.width: 1
                border.color: config.stringValue("showPasswordButtonColor")
                color:  passwordBox.echoMode === TextInput.Normal ? config.stringValue("showPasswordButtonColor") : "transparent"
                opacity: passwordBox.text.length > 0 ? 1 : 0.6
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor;
                    onClicked: {
                        if(passwordBox.echoMode === TextInput.Password)
                           passwordBox.echoMode = TextInput.Normal
                        else
                           passwordBox.echoMode = TextInput.Password
                    }
                }
            }
        }
        Rectangle{
            Layout.fillWidth: true
            height: 1
            color: config.stringValue("passwordUnderlineColor")
        }
        Rectangle{
            Layout.fillWidth: true
            height: passwordBox.height * 2
            color: "transparent"
            Rectangle{

                anchors.topMargin: Kirigami.Units.gridUnit
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width * 0.75
                height: passwordBox.height * 1.5
                border.width: 1
                radius: 0
                border.color: passwordBox.text.length > 0 ? config.stringValue("loginButtonGoColor") : config.stringValue("loginButtonReadyColor")
                color: "transparent"
                id: loginButton
                opacity: passwordBox.text.length > 0 ? 1 : 0.9

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    color:  passwordBox.text.length > 0 ? config.stringValue("loginButtonGoColor") : config.stringValue("loginButtonReadyColor")
                    text: passwordBox.text.length > 0 ? "Go !" : "Ready"
                    font.pointSize: 20
                    font.family: newFont.name
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: {
                        if (passwordBox.text.length > 0)
                            Qt.PointingHandCursor
                    }
                    onClicked: {
                        if (passwordBox.text.length > 0)
                            startLogin();
                    }
                }
            }
            Glow {
                anchors.fill: loginButton
                samples: config.boolValue("loginButtonGlow") ? 17 : 0
                color: config.stringValue("loginButtonGoColor")
                source: loginButton
                visible:  passwordBox.text.length > 0
                spread: 0
            }
        }
    }
}
