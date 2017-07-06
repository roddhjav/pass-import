#!/usr/bin/env ruby

# Copyright (C) 2017 Will Fleming <will@flemi.ng>. All Rights Reserved.
# Released under MIT license.
#
# Import Enpass data into pass(1).
#
# Reads Enpass CSV exports. Supports OTP entries & arbitrary metadata, emits
# multiline format entries. Puts entries without passwords under a `notes/` dir.
#
# https://github.com/wfleming/enpass2pass

########################## Requires/Types ##########################

require "csv"
require "open3"
require "optparse"

Opts = Struct.new(:force, :filter, :dry_run)
$opts = Opts.new(false, false, false)

$opts_parser = OptionParser.new do |opts|
  opts.banner = "#{opts.program_name}.rb [options] filename"
  opts.on("-h", "--help") do
    puts opts.to_s
    exit
  end
  opts.on("-f", "--force", "Overwrite existing entries") { $opts.force = true }
  opts.on("--filter", "Filter noisy attributes") { $opts.filter = true }
  opts.on("--dry-run", "Don't actually import: print what would be done") do
    $opts.dry_run = true
  end
end

class Entry
  attr_reader :title, :note, :attrs

  def initialize(row)
    @title = row.shift
    @note = row.pop
    @attrs = build_attrs(row)
    @attrs = filtered_attrs if $opts.filter
  end

  # translate "title" to make it nicer as a filename
  def pass_filename
    fn = title.tr(" []()!?/", "-______-")
    if password
      fn
    else
      "notes/#{fn}"
    end
  end

  def to_pass
    e = ""
    e << "#{password}\n" if password
    e << "URL: #{url}\n" if url
    e << "Username: #{login}\n" if login
    e << "#{otp}\n" if otp
    e << misc_attrs.map { |k, v| "#{k}: #{v}\n" }.join("")
    e << "Note: #{note}\n" if note && !note.empty?
    e
  end

  private

  def build_attrs(row)
    attrs = Hash.new
    row.each_slice(2) do |pieces|
      attrs[pieces[0]] = pieces[1]
    end
    attrs
  end

  # filter out repetitive/uneeded fields that tend to get included from
  # entries created via browser plugin: there's always a chance this will rm
  # some fields you actually care about, so enable with caution!
  def filtered_attrs
    attrs.reject do |k, _|
      kd = k.downcase
      kd.empty? || kd.start_with?("html") || kd.include?("remember") ||
        kd == "persistent" || kd.include?("tos") || kd.include?("captcha") ||
        kd == "submit" || kd == "scope" || kd.include?("confirm")
    end
  end

  def password
    p = extract(%w[
      password pass .pw1 regPassword logonPassword pwd
    ])
    if p
      p
    else
      e = attrs.detect { |k, _|
        kd = k.downcase
        kd.include?("pass") && "o" != kd[0] && !kd.include?("old")
      }
      e && e[1]
    end
  end

  def login
    extract(%w[
      login username loginuser user userid uid email emailaddress regEmail
      user[email]
    ])
  end

  def url
    extract(%w[url])
  end

  def otp
    attrs["TOTP"]
  end

  # extract a field that may exist under many names with case insensitivity
  def extract(names)
    e = attrs.detect { |k, _| names.include?(k.downcase) }
    e && e[1]
  end

  def misc_attrs
    attrs.reject do |_, v|
      v.nil? || v.empty? || [password, login, url, otp].include?(v)
    end
  end
end

class PassImporter
  attr_reader :errors

  def initialize
    @errors = []
  end

  def import(entry)
    if $opts.dry_run
      puts "cmd=#{pass_cmd(entry).inspect} entry=\n#{entry.to_pass}\n\n"
      return
    end

    Open3.popen3(*pass_cmd(entry)) do |stdin, o, stderr, thr|
      stdin.puts(entry.to_pass)
      stdin.close

      if 0 == thr.value
        puts "Imported '#{entry.title}' to '#{entry.pass_filename}'"
        return true
      else
        errors << "Error importing #{entry.title} (#{stderr.read})"
        return false
      end
    end
  end

  private

  def pass_cmd(entry)
    [
     "pass",
     "insert",
     "--multiline",
     ("--force" if $opts.force),
     entry.pass_filename
    ].compact
  end
end

########################## Run logic ##########################

begin
  $opts_parser.parse!
rescue OptionParser::InvalidOption
  $stderr.puts $opts_parser.to_s
  exit 1
end

$input_path = ARGV.pop

unless $input_path && File.exist?($input_path)
  $stderr.puts $opts_parser.to_s
  exit 1
end

imported = 0
importer = PassImporter.new
csv = CSV.open($input_path, headers: false)
csv.each_with_index do |row, idx|
  next if idx == 0
  entry = Entry.new(row.to_a)
  imported += 1 if importer.import(entry)
end

unless $opts.dry_run
  puts "Imported #{imported} entries\n"
end

if importer.errors.any?
  $stderr.puts "\nIMPORT ENCOUNTERED #{importer.errors.count} ERRORS:"
  importer.errors.each { |err| $stderr.puts err }
end
