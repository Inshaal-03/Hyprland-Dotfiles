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

import QtQuick 2.0
import QtQuick.Layouts 1.15

import org.kde.plasma.core 2.0
import org.kde.plasma.components 3.0
import Qt5Compat.GraphicalEffects
import org.kde.kirigami 2.20 as Kirigami

Item {
    id: clock

    property date timeSource: new Date()

    Label {
        id: label_mm
        text: Qt.formatTime(clock.timeSource, config.stringValue("timeFormat") === "12hours" ? "h:mm AP" : "hh:mm")
        font.pointSize: config.realValue("timeSize")
        renderType: Text.QtRendering
        anchors.top: parent.top
        anchors.left : parent.left
        anchors.leftMargin: Kirigami.Units.gridUnit
        anchors.topMargin: Kirigami.Units.gridUnit
        font.family: newFont.name
        color: config.stringValue("timeColor")
    }

    Glow {
        anchors.fill: label_mm
        samples: config.boolValue("timeGlow") ? 20 : 0
        color: config.stringValue("timeColor")
        source: label_mm
        spread: 0
    }

    Label {
        id : label_sub
        text: Qt.formatDate(clock.timeSource, config.stringValue("dateFormat"))
        font.pointSize: config.realValue("dateSize")
        anchors.top: parent.top
        anchors.right : parent.right
        anchors.rightMargin: Kirigami.Units.gridUnit
        anchors.topMargin: Kirigami.Units.gridUnit
        font.family: newFont.name
        color: config.stringValue("dateColor")
    }

    Glow {
        anchors.fill: label_sub
        samples: config.boolValue("dateGlow") ? 20 : 0
        color: config.stringValue("dateColor")
        source: label_sub
        spread: 0
    }
}
