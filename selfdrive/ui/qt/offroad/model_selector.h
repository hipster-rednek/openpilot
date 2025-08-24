// MIT Non-Commercial License
//
// Copyright (c) 2019, dragonpilot
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, for non-commercial purposes only, subject to the following conditions:
//
// - The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
// - Commercial use (e.g., use in a product, service, or activity intended to generate revenue) is prohibited without explicit written permission from dragonpilot. Contact ricklan@gmail.com for inquiries.
// - Any project that uses the Software must visibly mention the following acknowledgment: "This project uses software from dragonpilot and is licensed under a custom license requiring permission for use."
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#pragma once

#include <QWidget>
#include <QPushButton>
#include <QListWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QListWidgetItem>
#include <QDebug>
#include <QStackedWidget>
#include <QButtonGroup>  // Add this include for QButtonGroup
#include <QEvent>
#include "common/params.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

class ModelSelector : public QWidget {
    Q_OBJECT

public:
    explicit ModelSelector(QWidget *parent = nullptr);

    // Get the model list panel widget
    QWidget* getModelListPanel();

    // Set the panel widget to switch to when selecting models
    void setPanelWidget(QStackedWidget* panel);

    // Set the button group to return to after model selection
    void setNavButtonGroup(QButtonGroup* nav_btns);

signals:
    void buttonClicked();
    void modelSelected(const QString& model_name);

private:
    QPushButton* model_selector_btn;
    QListWidget* model_list;
    QWidget* model_list_panel;
    ScrollView* model_list_frame;
    QStackedWidget* panel_widget = nullptr;
    QButtonGroup* nav_btns = nullptr;

    QWidget* setupUI();
    void setupModelListPanel();
    void loadModelList();
    void updateCurrentSelection();
    void clearModelList();
    void connectSignals();
    void updateButtonText(const QString& text);

protected:
    bool eventFilter(QObject *obj, QEvent *event) override;
};
