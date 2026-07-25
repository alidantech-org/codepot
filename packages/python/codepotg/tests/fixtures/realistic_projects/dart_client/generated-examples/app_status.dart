// Representative output generated from the canonical AppStatus schema.
import 'package:json_annotation/json_annotation.dart';

enum AppStatus {
  @JsonValue('active')
  active,
  @JsonValue('suspended')
  suspended,
  @JsonValue('disabled')
  disabled
}
