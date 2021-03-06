#!/usr/bin/env python
# Copyright 2014 Scalyr Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
#
# Contains the data structures used to represent a snapshot of the
# agent's status, giving such details as the number of log bytes copied,
# whether or not the configuration file was successfully parsed, etc.
#
# These data structures are generated by the ScalyrAgent's __generate_status
# method and are used to create both the interactive status (which is emitted when
# the 'status -v' command is invoked by the user) and the status periodically recorded
# in the agent log.
#
# author: Steven Czerwinski <czerwin@scalyr.com>

from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

__author__ = "czerwin@scalyr.com"

import os
import copy

import scalyr_agent.util as scalyr_util
from scalyr_agent import compat

import six


class BaseAgentStatus(object):
    """
    Base agent status class which implements "to_dict()" method.
    """

    def to_dict(self):
        # type: () -> dict
        """
        Return dictionary version of the status object. This dictionary contains only simple /
        native values and is JSON serializable.
        """
        result = copy.deepcopy(self.__dict__)

        # Recursively convert nested objects to dicts
        for key, value in result.items():
            if isinstance(value, (list, tuple)):
                items = []
                for item in value:
                    if hasattr(item, "to_dict"):
                        item = item.to_dict()
                    items.append(item)
                result[key] = items
            elif isinstance(value, dict):
                for item_key, item_value in value.items():
                    if hasattr(item_value, "to_dict"):
                        item_value = item_value.to_dict()
                    result[key][item_key] = item_value
            elif hasattr(value, "to_dict"):
                result[key] = value.to_dict()

        return result


class AgentStatus(BaseAgentStatus):
    """The main status container object, holding references to all other status elements.
    """

    def __init__(self):
        # The time (in seconds past epoch) when the agent process was launched.
        self.launch_time = None
        # The user name the agent process is running under.
        self.user = None
        # The version string for the agent.
        self.version = None
        # The name of the host the agent is running on.
        self.server_host = None
        # The URL of the scalyr server that the agent is connected to (such as https://www.scalyr.com/).
        self.scalyr_server = None
        # The path for the agent's log file.
        self.log_path = None
        # The ConfigStatus object recording the status for the configuration file.
        self.config_status = None
        # The CopyingManagerStatus object recording the status of the log copying manager (or none if CopyingManager
        # has not been started). This contains information about the different log paths being watched and the
        # progress of copying their bytes.
        self.copying_manager_status = None
        # The MonitorManagerStatus object recording the status of the monitor manager (or none if the MonitorManager
        # has not been started).  This contains information about the different ScalyrMonitors being run.
        self.monitor_manager_status = None


class GCStatus(BaseAgentStatus):
    """
    Class which holds garbage collection statistics.

    Those stats are disabled by default because they have an impact on memory usage so they must
    be explicitly enabled.
    """

    def __init__(self):
        # This metric indicates number of objects which are unreachable but can't be freed.
        self.garbage = 0

    def to_dict(self):
        return self.__dict__


class OverallStats(AgentStatus):
    """Used to track stats that are calculated over the lifetime of the agent.
    """

    def __init__(self):
        # The time in seconds past epoch when the agent was started.
        self.launch_time = None
        # The version string for the agent.
        self.version = None
        # The current number of paths the log copier is watching.
        self.num_watched_paths = 0
        # The current number of file paths the log copier is copying.
        self.num_copying_paths = 0
        # The current number of running monitors.
        self.num_running_monitors = 0
        # The current number of monitors that should be running but are not.
        self.num_dead_monitor = 0
        # The total amount of user time CPU used by the agent (cpu secs).
        self.user_cpu = 0
        # The total amount of system time CPU used by the agent (cpu secs)
        self.system_cpu = 0
        # The current resident size in bytes of the agent process.
        self.rss_size = 0

        # The total number of log bytes copied to the Scalyr servers.
        self.total_bytes_copied = 0
        # The total number of log bytes that were skipped and were not considered to be sent to the Scalyr servers.
        self.total_bytes_skipped = 0
        # The total number of log bytes that were not sent to the Scalyr servers due to subsampling rules.
        self.total_bytes_subsampled = 0
        # The total number of log bytes that were not sent to Scalyr due to errors on either the client or server side.
        self.total_bytes_failed = 0
        # The total number of redactions that were applied to the log lines before being sent to the Scalyr servers.
        self.total_redactions = 0
        # The total number of errors seen when issuing a copy request.
        self.total_copy_requests_errors = 0
        # The total number of lines reported by monitors.
        self.total_monitor_reported_lines = 0
        # The total number of errors seen by executing monitors.
        self.total_monitor_errors = 0

        # The total number of RPC requests sent.
        self.total_requests_sent = 0
        # The total number of RPC requests that failed.
        self.total_requests_failed = 0
        # The total number of bytes sent over the network.
        self.total_request_bytes_sent = 0
        # The total number of compressed bytes sent over the network.
        self.total_compressed_request_bytes_sent = 0
        # The total number of bytes received.
        self.total_response_bytes_received = 0
        # The total number of secs spent waiting for a responses (so average latency can be calculated by dividing
        # this number by self.total_requests_sent).  This includes connection establishment time.
        self.total_request_latency_secs = 0
        # The total number of HTTP connections successfully created.
        self.total_connections_created = 0

    def __add__(self, other):
        """Adds all of the 'total_' fields of this instance and other together and returns a new OverallStats containing
        the result.
        """
        result = OverallStats()
        result.total_bytes_copied = self.total_bytes_copied + other.total_bytes_copied
        result.total_bytes_skipped = (
            self.total_bytes_skipped + other.total_bytes_skipped
        )
        result.total_bytes_subsampled = (
            self.total_bytes_subsampled + other.total_bytes_subsampled
        )
        result.total_bytes_failed = self.total_bytes_failed + other.total_bytes_failed
        result.total_redactions = self.total_redactions + other.total_redactions
        result.total_copy_requests_errors = (
            self.total_copy_requests_errors + other.total_copy_requests_errors
        )
        result.total_monitor_reported_lines = (
            self.total_monitor_reported_lines + other.total_monitor_reported_lines
        )
        result.total_monitor_errors = (
            self.total_monitor_errors + other.total_monitor_errors
        )

        result.total_requests_sent = (
            self.total_requests_sent + other.total_requests_sent
        )
        result.total_requests_failed = (
            self.total_requests_failed + other.total_requests_failed
        )
        result.total_request_bytes_sent = (
            self.total_request_bytes_sent + other.total_request_bytes_sent
        )
        result.total_compressed_request_bytes_sent = (
            self.total_compressed_request_bytes_sent
            + other.total_compressed_request_bytes_sent
        )
        result.total_response_bytes_received = (
            self.total_response_bytes_received + other.total_response_bytes_received
        )
        result.total_request_latency_secs = (
            self.total_request_latency_secs + other.total_request_latency_secs
        )
        result.total_connections_created = (
            self.total_connections_created + other.total_connections_created
        )

        return result


class ConfigStatus(BaseAgentStatus):
    """The status pertaining to parsing of the configuration file."""

    def __init__(self):
        # The path of the configuration file.
        self.path = None
        # The paths for additional configuration files read from the config directory.
        self.additional_paths = []
        # The last time the configuration file changed and was read by this agent.
        self.last_read_time = None
        # A status line describing if the configuration file was successfully parsed.
        self.status = None
        # If the status file count not be parsed/used, a string describing the error.
        self.last_error = None
        # The last time the configuration file was successfully parsed.
        self.last_good_read = None
        # The last time the agent checked to see if the configuration file has changed.
        self.last_check_time = None

    def to_dict(self):
        return self.__dict__


class CopyingManagerStatus(BaseAgentStatus):
    """The status object containing information about the agent's copying components."""

    def __init__(self):
        # The total number of bytes successfully uploaded.
        self.total_bytes_uploaded = 0
        # The last time the agent successfully copied bytes from log files to the Scalyr servers.
        self.last_success_time = None
        # The last time the agent attempted to copy bytes from log files to the Scalyr servers.
        self.last_attempt_time = None
        # The size of the request for the last attempt.
        self.last_attempt_size = None
        # The last response from the Scalyr servers.
        self.last_response = None
        # The last status from the last response (should be 'success').
        self.last_response_status = None
        # The total number of failed copy requests.
        self.total_errors = None

        # LogMatcherStatus objects for each of the log paths being watched for copying.
        self.log_matchers = []


class LogMatcherStatus(BaseAgentStatus):
    """The status object containing information about all of the copying being performed for a particular
    log path including globbing."""

    def __init__(self):
        # The path.
        self.log_path = None
        # True if the log path contains globbing characters.
        self.is_glob = None
        # The last time the agent checked the path for new matches.
        self.last_check_time = None
        # For any matching file paths, a LogProcessorStatus object describing the copying.
        self.log_processors_status = []


class LogProcessorStatus(BaseAgentStatus):
    """The status object containing information about the progress of the bytes being copied for a particular
    file."""

    def __init__(self):
        # The path of the file (will not contain glob characters).  This will be a path to an existing file.
        self.log_path = None
        # The last time the file was checked for new bytes.
        self.last_scan_time = None
        # The total bytes copied to the Scalyr servers.
        self.total_bytes_copied = 0
        # The number of bytes that still need to be sent to the Scalyr servers.
        self.total_bytes_pending = 0
        # The total bytes that were skipped (due to the log lines being too old, or the agent falling behind).
        self.total_bytes_skipped = 0
        # The total bytes that failed due to errors at either the server or client.
        self.total_bytes_failed = 0
        # The total bytes that were not sent to the server due to subsampling rules.
        self.total_bytes_dropped_by_sampling = 0
        # The total number of log lines copied to the Scalyr servers.
        self.total_lines_copied = 0
        # The total number of log lines that were not sent to the server due to subsampling rules.
        self.total_lines_dropped_by_sampling = 0
        # The total number of redactions applied to the log lines copied to the server.
        self.total_redactions = 0


class MonitorManagerStatus(BaseAgentStatus):
    """The status object containing information about all of the running monitors."""

    def __init__(self):
        # The total number of monitors that are currently running.
        self.total_alive_monitors = 0
        # The MonitorStatus object for each monitor that is currently running or should be running.
        self.monitors_status = []


class MonitorStatus(BaseAgentStatus):
    """The status object for a specific instance of a ScalyrMonitor."""

    def __init__(self):
        # The name of the monitor.
        self.monitor_name = None
        # The total number of metric lines reported by the monitor.
        self.reported_lines = 0
        # The total number of errors produced by the monitor.
        self.errors = 0
        # Whether or not the monitor is running.
        self.is_alive = False


def report_status(output, status, current_time):
    print(
        "Scalyr Agent status.  See https://www.scalyr.com/help/scalyr-agent-2 for help",
        file=output,
    )
    print("", file=output)
    print("Current time:     %s" % scalyr_util.format_time(current_time), file=output)
    print(
        "Agent started at: %s" % scalyr_util.format_time(status.launch_time),
        file=output,
    )
    print("Version:          %s" % status.version, file=output)
    print("Agent running as: %s" % status.user, file=output)
    print("Agent log:        %s" % status.log_path, file=output)
    print("ServerHost:       %s" % status.server_host, file=output)
    print("", file=output)
    server = status.scalyr_server
    # We default to https://agent.scalyr.com for the Scalyr server, but to see the status on the web,
    # you should go to https://www.scalyr.com.  So, we do a little clean up before sticking it in
    # the url.  Same goes for https://log.scalyr.com  -- it is really is just https://www.scalyr.com
    server = server.replace("https://agent.", "https://www.")
    server = server.replace("https://log.", "https://www.")
    print(
        "View data from this agent at: %s/events?filter=$serverHost%%3D%%27%s%%27"
        % (server, status.server_host,),
        file=output,
    )
    print("", file=output)
    print("", file=output)

    # Configuration file status:
    print("Agent configuration:", file=output)
    print("====================", file=output)
    print("", file=output)
    if len(status.config_status.additional_paths) == 0:
        print("Configuration file:    %s" % status.config_status.path, file=output)
    else:
        print("Configuration files:   %s" % status.config_status.path, file=output)
        for x in status.config_status.additional_paths:
            print("                       %s" % x, file=output)

    if status.config_status.last_error is None:
        print("Status:                Good (files parsed successfully)", file=output)
    else:
        print(
            "Status:                Bad (could not parse, using last good version)",
            file=output,
        )
    print(
        "Last checked:          %s"
        % scalyr_util.format_time(status.config_status.last_check_time),
        file=output,
    )
    print(
        "Last changed observed: %s"
        % scalyr_util.format_time(status.config_status.last_read_time),
        file=output,
    )

    if status.config_status.last_error is not None:
        print(
            "Parsing error:         %s"
            % six.text_type(status.config_status.last_error),
            file=output,
        )

    def print_environment():

        # Print scalyr-related env variables in sorted order with critical variables up top. Redact API key.
        main_keys = ["SCALYR_API_KEY", "SCALYR_SERVER"]
        special_case_keys = set(["K8S_EVENT_DISABLE"])
        redacted_keys = set(["SCALYR_API_KEY"])

        # Make a map of uppercase keys -> relevant environment vars (beginning with SCALYR)
        upper2actualkey = {}
        for k in os.environ.keys():
            kup = k.upper()
            if kup.startswith("SCALYR") or kup in special_case_keys:
                upper2actualkey[kup] = k

        # Sorted list of all scalyr keys, including main_keys which may not be present
        # Sort order does not consider letter case.
        sorted_upperkeys = main_keys + sorted(
            set(upper2actualkey.keys()) - set(main_keys)
        )

        print("", file=output)
        row = 0
        for kup in sorted_upperkeys:
            key = upper2actualkey.get(kup, kup)
            val = compat.os_getenv_unicode(key)
            if not val:
                val = "<Missing>"
            elif key.upper() in redacted_keys:
                val = "<Redacted>"

            if row == 0:
                print("Environment variables: %s = %s" % (key, val), file=output)
            else:
                print("                       %s = %s" % (key, val), file=output)
            row += 1

    print_environment()

    if status.copying_manager_status is not None:
        print("", file=output)
        print("", file=output)
        __report_copying_manager(
            output,
            status.copying_manager_status,
            status.log_path,
            status.config_status.last_read_time,
        )

    if status.monitor_manager_status is not None:
        print("", file=output)
        print("", file=output)
        __report_monitor_manager(
            output, status.monitor_manager_status, status.config_status.last_read_time
        )


def __report_copying_manager(output, manager_status, agent_log_file_path, read_time):
    print("Log transmission:", file=output)
    print("=================", file=output)
    print("", file=output)
    print(
        "(these statistics cover the period from %s)"
        % scalyr_util.format_time(read_time),
        file=output,
    )
    print("", file=output)

    print(
        "Bytes uploaded successfully:               %ld"
        % manager_status.total_bytes_uploaded,
        file=output,
    )
    print(
        "Last successful communication with Scalyr: %s"
        % scalyr_util.format_time(manager_status.last_success_time),
        file=output,
    )
    print(
        "Last attempt:                              %s"
        % scalyr_util.format_time(manager_status.last_attempt_time),
        file=output,
    )
    if manager_status.last_attempt_size is not None:
        print(
            "Last copy request size:                    %ld"
            % manager_status.last_attempt_size,
            file=output,
        )
    if manager_status.last_response is not None:
        print(
            "Last copy response size:                   %ld"
            % len(manager_status.last_response),
            file=output,
        )
        print(
            "Last copy response status:                 %s"
            % manager_status.last_response_status,
            file=output,
        )
        if manager_status.last_response_status != "success":
            print(
                "Last copy response:                        %s"
                % scalyr_util.remove_newlines_and_truncate(
                    manager_status.last_response, 1000
                ),
                file=output,
            )
    if manager_status.total_errors > 0:
        print(
            "Total responses with errors:               %d (see '%s' for details)"
            % (manager_status.total_errors, agent_log_file_path,),
            file=output,
        )
    print("", file=output)

    for matcher_status in manager_status.log_matchers:
        if not matcher_status.is_glob:
            if len(matcher_status.log_processors_status) == 0:
                # This is an absolute file path (no wildcards) and there are not matches.
                print(
                    "Path %s: no matching readable file, last checked %s"
                    % (
                        matcher_status.log_path,
                        scalyr_util.format_time(matcher_status.last_check_time),
                    ),
                    file=output,
                )
            else:
                # We have a match.. matcher_status.log_processors_status should really only have one
                # entry, but we loop anyway.
                for processor_status in matcher_status.log_processors_status:
                    output.write(
                        "Path %s: copied %ld bytes (%ld lines), %ld bytes pending, "
                        % (
                            processor_status.log_path,
                            processor_status.total_bytes_copied,
                            processor_status.total_lines_copied,
                            processor_status.total_bytes_pending,
                        )
                    )
                    if processor_status.total_bytes_skipped > 0:
                        output.write(
                            "%ld bytes skipped, " % processor_status.total_bytes_skipped
                        )
                    if processor_status.total_bytes_failed > 0:
                        output.write(
                            "%ld bytes failed, " % processor_status.total_bytes_failed
                        )
                    if processor_status.total_bytes_dropped_by_sampling > 0:
                        output.write(
                            "%ld bytes dropped by sampling (%ld lines), "
                            % (
                                processor_status.total_bytes_dropped_by_sampling,
                                processor_status.total_lines_dropped_by_sampling,
                            )
                        )

                    if processor_status.total_redactions > 0:
                        output.write(
                            "%ld redactions, " % processor_status.total_redactions
                        )
                    output.write(
                        "last checked %s"
                        % scalyr_util.format_time(processor_status.last_scan_time)
                    )
                    output.write("\n")
                    output.flush()

    need_to_add_extra_line = True
    for matcher_status in manager_status.log_matchers:
        if matcher_status.is_glob:
            if need_to_add_extra_line:
                need_to_add_extra_line = False
                print("", file=output)
            print(
                "Glob: %s:: last scanned for glob matches at %s"
                % (
                    matcher_status.log_path,
                    scalyr_util.format_time(matcher_status.last_check_time),
                ),
                file=output,
            )

            for processor_status in matcher_status.log_processors_status:
                output.write(
                    "  %s: copied %ld bytes (%ld lines), %ld bytes pending, "
                    % (
                        processor_status.log_path,
                        processor_status.total_bytes_copied,
                        processor_status.total_lines_copied,
                        processor_status.total_bytes_pending,
                    )
                )
                if processor_status.total_bytes_skipped > 0:
                    output.write(
                        "%ld bytes skipped, " % processor_status.total_bytes_skipped
                    )
                if processor_status.total_bytes_failed > 0:
                    output.write(
                        "%ld bytes failed, " % processor_status.total_bytes_failed
                    )
                if processor_status.total_bytes_dropped_by_sampling > 0:
                    output.write(
                        "%ld bytes dropped by sampling (%ld lines), "
                        % (
                            processor_status.total_bytes_dropped_by_sampling,
                            processor_status.total_lines_dropped_by_sampling,
                        )
                    )

                if processor_status.total_redactions > 0:
                    output.write("%ld redactions, " % processor_status.total_redactions)
                output.write(
                    "last checked %s"
                    % scalyr_util.format_time(processor_status.last_scan_time)
                )
                output.write("\n")
                output.flush()


def __report_monitor_manager(output, manager_status, read_time):
    print("Monitors:", file=output)
    print("=========", file=output)
    print("", file=output)
    print(
        "(these statistics cover the period from %s)"
        % scalyr_util.format_time(read_time),
        file=output,
    )
    print("", file=output)
    if manager_status.total_alive_monitors < len(manager_status.monitors_status):
        print("Running monitors:", file=output)
        padding = "  "
    else:
        padding = ""

    for entry in manager_status.monitors_status:
        if entry.is_alive:
            print(
                "%s%s: %d lines emitted, %d errors"
                % (padding, entry.monitor_name, entry.reported_lines, entry.errors,),
                file=output,
            )

    dead_monitors = (
        len(manager_status.monitors_status) - manager_status.total_alive_monitors
    )
    if dead_monitors > 0:
        print("", file=output)
        print("Failed monitors:", file=output)
        for entry in manager_status.monitors_status:
            if not entry.is_alive:
                print(
                    "  %s %d lines emitted, %d errors"
                    % (entry.monitor_name, entry.reported_lines, entry.errors,),
                    file=output,
                )
