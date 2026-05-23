cube(`SpaceUtilization`, {
  sql: `SELECT * FROM coworkbooking.space_occupancy_5m`,

  measures: {
    SpaceUtilization: {
      sql: `people_delta`,
      type: `sum`,
      title: `Space Utilization Delta`
    },
    EventCount: {
      sql: `event_count`,
      type: `sum`
    }
  },

  dimensions: {
    spaceId: { sql: `space_id`, type: `string` },
    zone: { sql: `zone`, type: `string` },
    windowStart: { sql: `window_start`, type: `time` }
  }
});
