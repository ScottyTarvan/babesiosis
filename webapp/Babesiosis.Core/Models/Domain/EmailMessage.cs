using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Domain
{
    public class EmailMessage
    {
        public Guid UserId { get; set; }
        public MessageType MessageType { get; set; }

        // --- PipelineExpectationBreach only (plan §7) ---
        public int? PipelineId { get; set; }
        public List<long> EventIds { get; set; }
    }
}
