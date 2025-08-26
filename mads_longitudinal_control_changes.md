# MADS Longitudinal Control Changes

## Summary

Modified the Hyundai car controller to enable longitudinal control (SCC_CONTROL messages) when MADS is enabled via the LFA button, even if `openpilotLongitudinalControl` is not normally enabled.

## Key Changes

1. **Longitudinal Control Logic**: Added logic to check for MADS state when deciding whether to send longitudinal control messages:
   ```python
   send_longitudinal = self.CP.openpilotLongitudinalControl or self.mads.enable_mads
   ```

2. **Modified Areas**:
   - Tester present messages (line 102)
   - Button messages logic (line 146)
   - CAN message sending for non-CAN-FD vehicles (line 158)
   - CAN-FD message sending (line 201)
   - ACC options sending (line 172)
   - Front radar options sending (line 176)

3. **Behavior**:
   - When MADS is enabled via the LFA button (regardless of experimental mode status), the system will:
     - Send SCC_CONTROL messages for longitudinal control
     - Send ACC options (SCC13, FCA12)
     - Send front radar options
     - Send tester present messages to keep relevant ECUs disabled
     - Prevent button messages (cancel/resume) from being sent
   - This works even when experimental mode is OFF, allowing longitudinal control whenever MADS is enabled

## Testing Recommendations

1. Test on a CAN-FD Hyundai vehicle with MADS enabled
2. Verify that pressing the LFA button enables both lateral and longitudinal control
3. Check that SCC_CONTROL messages are being sent at the correct frequency (50Hz)
4. Confirm that the vehicle responds to acceleration/deceleration commands
5. Test transitions between MADS enabled/disabled states