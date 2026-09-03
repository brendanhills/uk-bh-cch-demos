# Specification: Staff Unavailable Disruption Track

## Overview
Adds a new interactive disruption capability ("Simulate Sick Call / Staff Unavailable") to the Cymbal Children's Hospital (CCH) scheduling demo. When triggered, the system randomly selects an active staff member (Surgeon or Nurse) on the displayed day, marks them as unavailable/sick, and dynamically recalculates the weekly schedule across the 5-day horizon by re-assigning qualified off-duty staff or re-routing affected surgeries.

## Functional Requirements
1. **UI Disruption Button**:
   - Add a `Simulate Sick Call` button (`#btn-inject-sick`) inside the `⚡ UNPLANNED DISRUPTIONS` toolbar in `cch/index.html`.
2. **Staff Selection & Sick Call Logic**:
   - Randomly select a staff member (Surgeon or Nurse) who has assigned surgeries on `activeDay`.
   - Record the staff member's unavailability (`EVOLUTION_DATA.staffUnavailability`).
3. **Weekly Schedule Recalculation**:
   - Identify all surgeries assigned to the sick staff member on `activeDay`.
   - For each affected surgery, search for an available off-duty staff member with matching specialist skill (e.g., Pediatric Neuro, Cardiac, Orthopedic).
   - If no qualified replacement staff is available on `activeDay`, re-route the surgery to another open slot and available room across the 5-day horizon while enforcing minimum rest/fatigue constraints.
4. **Visual Feedback & Storytelling Insight**:
   - Display a notification badge and update staff roster card styling to show the staff member as `SICK / UNAVAILABLE`.
   - Add a new trace step to `EVOLUTION_DATA.traces` with insight title: `⚡ Dynamic Re-Plan: Sick Call (Staff Member)` and summary details explaining how many surgeries were re-assigned or re-routed.

## Non-Functional Requirements
- Instant response (< 1s recalculation in Demo Mode).
- Preserves professional CCH branding, muted slate color palette, and 54px Gantt row height.

## Acceptance Criteria
- Clicking `Simulate Sick Call` randomly picks a working staff member on the active day and marks them as sick.
- Surgeries assigned to that staff member are automatically covered by qualified staff or re-routed to open slots across the 5-day schedule.
- Automated unit test suite verifies sick call injection, skill matching, and weekly schedule recalculation without errors.

## Out of Scope
- Real-time phone SMS or email notifications to staff.
- Permanent removal of staff from the database backend.
