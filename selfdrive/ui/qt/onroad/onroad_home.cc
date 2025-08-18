#include "selfdrive/ui/qt/onroad/onroad_home.h"

#include <QPainter>
#include <QStackedLayout>

#include "common/params.h"

#include "selfdrive/ui/qt/util.h"

OnroadWindow::OnroadWindow(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout  = new QVBoxLayout(this);
  main_layout->setMargin(UI_BORDER_SIZE);
  QStackedLayout *stacked_layout = new QStackedLayout;
  stacked_layout->setStackingMode(QStackedLayout::StackAll);
  main_layout->addLayout(stacked_layout);

  nvg = new AnnotatedCameraWidget(VISION_STREAM_ROAD, this);

  QWidget * split_wrapper = new QWidget;
  split = new QHBoxLayout(split_wrapper);
  split->setContentsMargins(0, 0, 0, 0);
  split->setSpacing(0);
  split->addWidget(nvg);

  if (getenv("DUAL_CAMERA_VIEW")) {
    CameraWidget *arCam = new CameraWidget("camerad", VISION_STREAM_ROAD, this);
    split->insertWidget(0, arCam);
  }

  stacked_layout->addWidget(split_wrapper);

  alerts = new OnroadAlerts(this);
  alerts->setAttribute(Qt::WA_TransparentForMouseEvents, true);
  stacked_layout->addWidget(alerts);

  // setup stacking order
  alerts->raise();

  // Force Offroad toggle button overlay (top-right)
  force_offroad_btn = new QPushButton(tr("OFFROAD"), this);
  force_offroad_btn->setFixedSize(360, 120);
  force_offroad_btn->setStyleSheet("font-size: 48px; font-weight: 600; color: white; background-color: #C92A2A; border: none; border-radius: 12px;");
  force_offroad_btn->raise();
  force_offroad_btn->move(width() - force_offroad_btn->width() - UI_BORDER_SIZE, UI_BORDER_SIZE);
  force_offroad_btn->show();
  connect(force_offroad_btn, &QPushButton::clicked, [this] {
    Params params;
    bool force = params.getBool("ForceOffroad");
    params.putBool("ForceOffroad", !force);
    // Immediately reflect label/color; actual transition occurs via hardwared started logic
    if (!force) {
      force_offroad_btn->setText(tr("ONROAD"));
      force_offroad_btn->setStyleSheet("font-size: 48px; font-weight: 600; color: white; background-color: #2B8A3E; border: none; border-radius: 12px;");
    } else {
      force_offroad_btn->setText(tr("OFFROAD"));
      force_offroad_btn->setStyleSheet("font-size: 48px; font-weight: 600; color: white; background-color: #C92A2A; border: none; border-radius: 12px;");
    }
  });

  setAttribute(Qt::WA_OpaquePaintEvent);
  QObject::connect(uiState(), &UIState::uiUpdate, this, &OnroadWindow::updateState);
  QObject::connect(uiState(), &UIState::offroadTransition, this, &OnroadWindow::offroadTransition);
}

void OnroadWindow::updateState(const UIState &s) {
  if (!s.scene.started) {
    return;
  }

  alerts->updateState(s);
  nvg->updateState(s);

  QColor bgColor = bg_colors[s.status];
  if (bg != bgColor) {
    // repaint border
    bg = bgColor;
    update();
  }

  // keep overlay button positioned in top-right on resize or state updates
  if (force_offroad_btn != nullptr) {
    force_offroad_btn->move(width() - force_offroad_btn->width() - UI_BORDER_SIZE, UI_BORDER_SIZE);
    // Sync label with param in case it's changed elsewhere
    Params params;
    bool force = params.getBool("ForceOffroad");
    if (force && force_offroad_btn->text() != tr("ONROAD")) {
      force_offroad_btn->setText(tr("ONROAD"));
      force_offroad_btn->setStyleSheet("font-size: 48px; font-weight: 600; color: white; background-color: #2B8A3E; border: none; border-radius: 12px;");
    } else if (!force && force_offroad_btn->text() != tr("OFFROAD")) {
      force_offroad_btn->setText(tr("OFFROAD"));
      force_offroad_btn->setStyleSheet("font-size: 48px; font-weight: 600; color: white; background-color: #C92A2A; border: none; border-radius: 12px;");
    }
  }
}

void OnroadWindow::offroadTransition(bool offroad) {
  alerts->clear();
}

void OnroadWindow::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.fillRect(rect(), QColor(bg.red(), bg.green(), bg.blue(), 255));
}
