#include "selfdrive/ui/qt/offroad/dp_panel.h"

void DPPanel::add_toyota_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("Toyota / Lexus"),
      "",
    },
    {
      "dp_toyota_door_auto_lock_unlock",
      tr("Enable Door Auto Lock/Unlock"),
      "",
    },
    {
      "dp_toyota_tss1_sng",
      tr("Enable TSS1 SnG Mod"),
      "",
    },
    {
      "dp_toyota_stock_lon",
      tr("Use Stock Longitudinal Control"),
      "",
    },
  };

  QWidget *label = nullptr;
  bool has_toggle = false;

  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

void DPPanel::add_vag_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("VW / Audi / Skoda"),
      "",
    },
    {
      "dp_vag_a0_sng",
      tr("Enable MQB A0 SnG Mod"),
      "",
    },
    {
      "dp_vag_pq_steering_patch",
      tr("PQ Steering Patch"),
      ""
    },
    {
      "dp_vag_avoid_eps_lockout",
      tr("Avoid EPS Lockout"),
      "",
    },
  };

  QWidget *label = nullptr;
  bool has_toggle = false;

  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

void DPPanel::add_mazda_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("Mazda"),
      "",
    },
  };

  QWidget *label = nullptr;
  bool has_toggle = false;

  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

void DPPanel::add_lateral_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("Lateral Ctrl"),
      "",
    },
    {
      "dp_lat_alka",
      tr("Always-on Lane Keeping Assist (ALKA)"),
      "",
    },
    {
      "dp_lat_road_edge_detection",
      tr("Road Edge Detection (RED)"),
      tr("Block lane change assist when the system detects the road edge.\nNOTE: This will show 'Car Detected in Blindspot' warning.")
    },
  };
  auto lca_speed_toggle = new ParamSpinBoxControl("dp_lat_lca_speed", tr("LCA Speed:"), tr("Off = Disable LCA\n1 mph ≈ 1.2 km/h"), "", 0, 100, 5, tr(" mph"), tr("Off"));
  lca_sec_toggle = new ParamDoubleSpinBoxControl("dp_lat_lca_auto_sec", QString::fromUtf8("　") + tr("Auto Lane Change after:"), tr("Off = Disable Auto Lane Change."), "", 0, 5.0, 0.5, tr(" sec"), tr("Off"));

  // Torque tuning parameters (advanced)
  auto torque_lat_accel_factor = new ParamDoubleSpinBoxControl(
      "dp_torque_lat_accel_factor",
      QString::fromUtf8("　") + tr("LAT_ACCEL_FACTOR:"),
      tr("Scaling from desired lateral accel to steering torque. Higher = more immediate authority."),
      "",
      1.0, 5.0, 0.01, "");
  auto torque_max_lat_accel_measured = new ParamDoubleSpinBoxControl(
      "dp_torque_max_lat_accel_measured",
      QString::fromUtf8("　") + tr("MAX_LAT_ACCEL_MEASURED:"),
      tr("Upper capability limit used for tuning and safety checks (m/s²)."),
      "",
      1.0, 4.0, 0.01, tr(" m/s²"));
  auto torque_friction = new ParamDoubleSpinBoxControl(
      "dp_torque_friction",
      QString::fromUtf8("　") + tr("FRICTION:"),
      tr("Static friction compensation in steering model. Lower = softer on-center, too low can cause wander."),
      "",
      0.01, 0.5, 0.005, "");

  QWidget *label = nullptr;
  bool has_toggle = false;

  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      addItem(lca_speed_toggle);
      addItem(lca_sec_toggle);
      // Add advanced torque tuning controls
      addItem(torque_lat_accel_factor);
      addItem(torque_max_lat_accel_measured);
      addItem(torque_friction);
      has_toggle = true;
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

void DPPanel::add_longitudinal_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("Longitudinal Ctrl"),
      "",
    },
    {
      "dp_lon_ext_radar",
      tr("Use External Radar"),
      tr("See https://github.com/eFiniLan/openpilot-ext-radar-addon for more information."),
    },
    {
      "dp_lon_acm",
      QString::fromUtf8("🚧 ") + tr("Enable Adaptive Coasting Mode (ACM)"),
      tr("Adaptive Coasting Mode (ACM) reduces braking to allow smoother coasting when appropriate.\nDOES NOT WORK with Experimental Mode enabled."),
    },
    {
      "dp_lon_acm_downhill",
      QString::fromUtf8("　") + tr("Downhill Only"),
      tr("Limited to downhill driving."),
    },
    {
      "dp_lon_aem",
      QString::fromUtf8("🚧 ") + tr("Adaptive Experimental Mode (AEM)"),
      tr("Adaptive mode switcher between ACC and Blended based on driving context."),
    },
    {
      "dp_lon_no_gas_gating",
      tr("Enable No Gas Gating (NoGG)"),
      tr("Allows the car to accelerate in situations where Gas Gating would normally prevent it, like approaching traffic lights or exits."),
    },
  };

  QWidget *label = nullptr;
  bool has_toggle = false;

  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      continue;
    }
    if (param == "dp_lon_ext_radar") {
      if (!vehicle_has_radar_unavailable || !vehicle_has_long_ctrl) {
        continue;
      }
    }
    if ((param == "dp_lon_acm" || param == "dp_lon_acm_downhill") && !vehicle_has_long_ctrl) {
      continue;
    }
    if (param == "dp_lon_aem" && !vehicle_has_long_ctrl) {
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

void DPPanel::add_ui_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("UI"),
      "",
    },
    {
      "dp_ui_radar_tracks",
      tr("Display Radar Tracks"),
      "",
    },
    {
      "dp_ui_rainbow",
      tr("Rainbow Driving Path like Tesla"),
      tr("Why not?"),
    },
  };
  std::vector<QString> display_off_mode_texts{tr("Std."), tr("MAIN+"), tr("OP+"), tr("MAIN-"), tr("OP-")};
  ButtonParamControl* display_off_mode_setting = new ButtonParamControl("dp_ui_display_mode", tr("Display Mode"),
                                          tr("Std. - Stock behavior.\nMAIN+ - ACC MAIN on = Display ON.\nOP+ - OP enabled = Display ON.\nMAIN- - ACC MAIN on = Display OFF\nOP- - OP enabled = Display OFF."),
                                          "",
                                          display_off_mode_texts, 200);
  auto hide_hud = new ParamSpinBoxControl("dp_ui_hide_hud_speed_kph", tr("Hide HUD When Moves above:"), tr("To prevent screen burn-in, hide Speed, MAX Speed, and Steering/DM Icons when the car moves.\nOff = Stock Behavior\n1 km/h ≈ 0.6 mph"), "", 0, 120, 5, tr(" km/h"), tr("Off"));

  QWidget *label = nullptr;
  bool has_toggle = false;

  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      addItem(display_off_mode_setting);
      has_toggle = true;
      addItem(hide_hud);
      has_toggle = true;
      continue;
    }
    if (param == "dp_ui_radar_tracks" && !vehicle_has_long_ctrl) {
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

void DPPanel::add_device_toggles() {
  std::vector<std::tuple<QString, QString, QString>> toggle_defs{
    {
      "",
      QString::fromUtf8("🐉 ") + tr("Device"),
      "",
    },
    {
      "dp_device_is_rhd",
      tr("Enable Right-Hand Drive Mode"),
      tr("Allow openpilot to obey right-hand traffic conventions on right driver seat."),
    },
    {
      "dp_device_monitoring_disabled",
      tr("Disable Driver Monitoring"),
      "",
    },
    {
      "dp_device_beep",
      tr("Enable Beep (Warning)"),
      "",
    }
  };
  std::vector<QString> audible_alert_mode_texts{tr("Std."), tr("Warning"), tr("Off")};
  ButtonParamControl* audible_alert_mode_setting = new ButtonParamControl("dp_device_audible_alert_mode", tr("Audible Alert Mode"),
                                          tr("Warning - Only emits sound when there is a warning.\nOff - Does not emit any sound at all."),
                                          "",
                                          audible_alert_mode_texts);

  auto auto_shutdown_toggle = new ParamSpinBoxControl("dp_device_auto_shutdown_in", tr("Auto Shutdown In:"), tr("0 mins = Immediately"), "", -5, 300, 5, tr(" mins"), tr("Off"));

  QWidget *label = nullptr;
  bool has_toggle = false;

  const bool disable_driver = getenv("DISABLE_DRIVER");
  for (auto &[param, title, desc] : toggle_defs) {
    if (param.isEmpty()) {
      label = new LabelControl(title, "");
      addItem(label);
      addItem(auto_shutdown_toggle);
      continue;
    }
    if ((param == "dp_device_is_rhd" || param == "dp_device_monitoring_disabled" || param == "dp_device_beep") && !disable_driver) {
      continue;
    }

    has_toggle = true;
    auto toggle = new ParamControl(param, title, desc, "", this);
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);
    addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }
  if (!getenv("DISABLE_DRIVER")) { // lite check
    addItem(audible_alert_mode_setting);
    has_toggle = true;
  }

  // If no toggles were added, hide the label
  if (!has_toggle && label) {
    label->hide();
  }
}

DPPanel::DPPanel(SettingsWindow *parent) : ListWidget(parent) {
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    brand = QString::fromStdString(CP.getBrand());
    vehicle_has_long_ctrl = hasLongitudinalControl(CP);
    vehicle_has_radar_unavailable = CP.getRadarUnavailable();

    // Seed default torque tuning DP params from current CarParams if not set yet
    try {
      const std::string k_lat = "dp_torque_lat_accel_factor";
      const std::string k_max = "dp_torque_max_lat_accel_measured";
      const std::string k_fric = "dp_torque_friction";

      if (params.get(k_lat).empty() || params.get(k_fric).empty() || params.get(k_max).empty()) {
        if (CP.getLateralTuning().isTorque()) {
          const auto torque = CP.getLateralTuning().getTorque();
          const double lat_factor = torque.getLatAccelFactor();
          const double friction = torque.getFriction();
          const double max_lat = CP.getMaxLateralAccel();

          if (params.get(k_lat).empty()) params.put(k_lat, std::to_string(lat_factor));
          if (params.get(k_fric).empty()) params.put(k_fric, std::to_string(friction));
          if (params.get(k_max).empty()) params.put(k_max, std::to_string(max_lat));
        }
      }
    } catch (...) {
      // ignore seeding errors
    }
  }

  if (brand == "toyota") {
    add_toyota_toggles();
  } else if (brand == "volkswagen") {
    add_vag_toggles();
  } else if (brand == "mazda") {
    add_mazda_toggles();
  }
  add_lateral_toggles();
  add_longitudinal_toggles();
  add_ui_toggles();
  add_device_toggles();

  auto resetBtn = new ButtonControl(tr("Reset dragonpilot settings"), tr("RESET"));
  connect(resetBtn, &ButtonControl::clicked, [&]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reset all settings?"), tr("Reset"), this)) {
      params.putBool("dp_device_reset_conf", true);
    }
  });
  addItem(resetBtn);

  fs_watch = new ParamWatcher(this);
  QObject::connect(fs_watch, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateStates();
  });

  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    is_onroad = !offroad;
    updateStates();
  });

  updateStates();
}

void DPPanel::showEvent(QShowEvent *event) {
  updateStates();
}

void DPPanel::updateStates() {
  // do fs_watch here
  fs_watch->addParam("dp_lat_lca_speed");
  fs_watch->addParam("dp_lon_acm");

  if (!isVisible()) {
    return;
  }

  // do state change logic here
  lca_sec_toggle->setVisible(std::atoi(params.get("dp_lat_lca_speed").c_str()) > 0);
  if (vehicle_has_long_ctrl) {
    toggles["dp_lon_acm_downhill"]->setVisible(params.getBool("dp_lon_acm"));
  }

}

void DPPanel::expandToggleDescription(const QString &param) {
  toggles[param.toStdString()]->showDescription();
}
