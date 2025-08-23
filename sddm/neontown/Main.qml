/*
 *   Copyright 2016 David Edmundson <davidedmundson@kde.org>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU Library General Public License as
 *   published by the Free Software Foundation; either version 2 or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details
 *
 *   You should have received a copy of the GNU Library General Public
 *   License along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

import QtQuick 2.2

import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects

import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.extras 2.0 as PlasmaExtras
import org.kde.plasma.private.keyboardindicator as KeyboardIndicator
import org.kde.kirigami 2.20 as Kirigami

import org.kde.breeze.components

import "components"

Item {
    id: root

    width: 1366
    height: 768

    property string notificationMessage

    LayoutMirroring.enabled: Qt.application.layoutDirection === Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    KeyboardIndicator.KeyState {
        id: capsLockState
        key: Qt.Key_CapsLock
    }

    Image {
        id: aBackground
        anchors.fill: parent
        source: config.stringValue("background")

    }

    FontLoader {
        id: newFont
        source: "assets/font/Cyberthrone.ttf"
    }

    Rectangle{
        id: rectangleBlur
        width: parent.width * 0.4
        height: parent.height * 0.4
        y: parent.height * 0.25

        anchors.horizontalCenter:  parent.horizontalCenter
        color: "transparent"
    }
    Rectangle {
        id: rectangleGlow
        anchors.fill: rectangleBlur
    }
    Glow {
        anchors.fill: rectangleGlow
        samples: config.boolValue("loginBorderGlow") ? 15 : 0
        color: config.stringValue("loginBorderGlowColor")
        source: rectangleGlow        
        spread: 0.3
    }
    ShaderEffectSource {
        id: effectSource
        sourceItem:       aBackground
        anchors.centerIn: rectangleBlur
        width:  rectangleBlur.width
        height: rectangleBlur.height
        sourceRect: Qt.rect(rectangleBlur.x,rectangleBlur.y, width, height)

    }
    FastBlur{
        id: blur
        anchors.fill: effectSource
        source: effectSource
        radius: config.boolValue("loginBackgroundBlur") ? config.realValue("loginBackgroundBlurRadius") : 0
    }
    ColorOverlay {
           anchors.fill: rectangleBlur
           source: blur
           color: config.stringValue("loginBackgroundColor")
     }

    Clock {
//      anchors.fill: parent
      anchors.fill: rectangleBlur
    }


    StackView {
        id: mainStack
        anchors {
            fill: rectangleBlur
        }

        focus: true //StackView is an implicit focus scope, so we need to give this focus so the item inside will have it

        Timer {
            //SDDM has a bug in 0.13 where even though we set the focus on the right item within the window, the window doesn't have focus
            //it is fixed in 6d5b36b28907b16280ff78995fef764bb0c573db which will be 0.14
            //we need to call "window->activate()" *After* it's been shown. We can't control that in QML so we use a shoddy timer
            //it's been this way for all Plasma 5.x without a huge problem
            running: true
            repeat: false
            interval: 200
            onTriggered: mainStack.forceActiveFocus()
        }

        initialItem: Login {
            id: userListComponent
            z:3
            userListModel: userModel
            userListCurrentIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
            lastUserName: userModel.lastUser
            showUserList: true
            notificationMessage: {
                const parts = [];
                if (capsLockState.locked) {
                    parts.push(i18nd("plasma-desktop-sddm-theme", "Caps Lock is on"));
                }
                if (root.notificationMessage) {
                    parts.push(root.notificationMessage);
                }
                return parts.join(" • ");
            }

            actionItems: [
                ActionButton {
                    iconSource: Qt.resolvedUrl("assets/images/suspend.svg")
                    text: i18nd("plasma_lookandfeel_org.kde.lookandfeel","Suspend")
                    onClicked: sddm.suspend()
                    enabled: sddm.canSuspend
                },
                ActionButton {
                    iconSource: Qt.resolvedUrl("assets/images/restart.svg")
                    text: i18nd("plasma_lookandfeel_org.kde.lookandfeel","Restart")
                    onClicked: sddm.reboot()
                    enabled: sddm.canReboot
                },
                ActionButton {
                    iconSource: Qt.resolvedUrl("assets/images/shutdown.svg")
                    text: i18nd("plasma_lookandfeel_org.kde.lookandfeel","Shutdown")
                    onClicked: sddm.powerOff()
                    enabled: sddm.canPowerOff
                }
            ]


            onLoginRequest: {
                root.notificationMessage = ""
                sddm.login(username, password, sessionButton.currentIndex)
            }
        }

        Behavior on opacity {
            OpacityAnimator {
                duration: Kirigami.Units.longDuration
            }
        }
    }

    //Footer
    RowLayout {
        id: footer
        anchors {
            top: parent.top
            topMargin: Kirigami.Units.gridUnit
            left: parent.left
            leftMargin: Kirigami.Units.gridUnit
            right: parent.right
            rightMargin: Kirigami.Units.gridUnit
        }

        Behavior on opacity {
            OpacityAnimator {
                duration: Kirigami.Units.longDuration
            }
        }

        SessionButton {
            id: sessionButton
        }

        Item {
            Layout.fillWidth: true
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            notificationMessage = i18nd("plasma_lookandfeel_org.kde.lookandfeel", "Login Failed")
        }
        function onLoginSucceeded() {
            //note SDDM will kill the greeter at some random point after this
            //there is no certainty any transition will finish, it depends on the time it
            //takes to complete the init
            mainStack.opacity = 0
            footer.opacity = 0
        }
    }

    onNotificationMessageChanged: {
        if (notificationMessage) {
            notificationResetTimer.start();
        }
    }

    Timer {
        id: notificationResetTimer
        interval: 3000
        onTriggered: notificationMessage = ""
    }

}
