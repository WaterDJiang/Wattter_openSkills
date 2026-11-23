import Vision
import AppKit
import Foundation

let args = CommandLine.arguments
guard args.count > 1 else { print("usage: wx_ocr <image>"); exit(1) }
let path = args[1]
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("NO_IMG"); exit(1)
}
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.recognitionLanguages = ["zh-Hans", "en-US"]
req.usesLanguageCorrection = true
try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
for obs in (req.results ?? []) {
    if let c = obs.topCandidates(1).first { print(c.string) }
}
