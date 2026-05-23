cube(`BookingOperations`, {
  sql: `SELECT * FROM coworkbooking.booking_revenue`,

  measures: {
    ClientCount: {
      sql: `client_id`,
      type: `countDistinct`,
      title: `Client Count`
    },
    TotalRevenue: {
      sql: `total_price`,
      type: `sum`,
      title: `Total Revenue`
    },
    AvgBookingValue: {
      sql: `total_price`,
      type: `avg`,
      title: `Average Booking Value`
    },
    BookingCount: {
      sql: `client_id`,
      type: `count`,
      title: `Bookings`
    }
  },

  dimensions: {
    clientId: { sql: `client_id`, type: `string`, primaryKey: true },
    segment: { sql: `segment`, type: `string` },
    city: { sql: `city`, type: `string` },
    spaceId: { sql: `space_id`, type: `string` },
    workplaceType: { sql: `workplace_type`, type: `string` },
    status: { sql: `status`, type: `string` },
    eventDate: { sql: `event_date`, type: `time` }
  }
});
