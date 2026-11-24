// osascript -l JavaScript cutout.js <in> <out.png> [largest|all|N]
// Lifts the foreground subject using Apple Vision; writes a cropped RGBA PNG.
ObjC.import('Foundation');ObjC.import('Vision');ObjC.import('CoreImage');ObjC.import('CoreVideo');ObjC.import('CoreGraphics');
function run(argv){
  const inURL=$.NSURL.fileURLWithPath(argv[0]),outURL=$.NSURL.fileURLWithPath(argv[1]),mode=argv[2]||'largest';
  const h=$.VNImageRequestHandler.alloc.initWithURLOptions(inURL,$({}));
  const req=$.VNGenerateForegroundInstanceMaskRequest.alloc.init;
  const err=Ref();
  if(!h.performRequestsError($([req]),err))return 'perform failed';
  if(req.results.count==0)return 'no subject';
  const obs=req.results.objectAtIndex(0);let inst=obs.allInstances;
  if(mode=='largest'&&inst.count>1){
    let best=-1,bestN=-1;let i=inst.firstIndex;
    while(i!=$.NSNotFound&&i<1e6){
      const one=$.NSIndexSet.indexSetWithIndex(i);
      const b=obs.generateMaskedImageOfInstancesFromRequestHandlerCroppedToInstancesExtentError(one,h,true,null);
      const n=$.CVPixelBufferGetWidth(b)*$.CVPixelBufferGetHeight(b);
      if(n>bestN){bestN=n;best=i;}
      i=inst.indexGreaterThanIndex(i);}
    inst=$.NSIndexSet.indexSetWithIndex(best);
  }else if(/^\d+$/.test(mode))inst=$.NSIndexSet.indexSetWithIndex(+mode);
  const buf=obs.generateMaskedImageOfInstancesFromRequestHandlerCroppedToInstancesExtentError(inst,h,true,null);
  const ci=$.CIImage.imageWithCVPixelBuffer(buf);
  const ctx=$.CIContext.context;
  const cs=$.CGColorSpaceCreateWithName($.kCGColorSpaceSRGB);
  const ok=ctx.writePNGRepresentationOfImageToURLFormatColorSpaceOptionsError(ci,outURL,$.kCIFormatRGBA8,cs,$({}),null);
  return (ok?'ok ':'write failed ')+obs.allInstances.count+' instances';
}
